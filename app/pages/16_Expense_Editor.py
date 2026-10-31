from __future__ import annotations

import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from datetime import date, timedelta
from utils.connection import get_db_connection
import psycopg2  # type: ignore
import os
from utils.data import (
    expense_category_options,
    fund_categories,
    payment_method,
    traveling_category_options,
)
from backend.trip_backend import fetch_all_trips

st.set_page_config(page_title="Expense Editor", page_icon="✏️", layout="wide")

DBT_SCHEMA = os.environ.get("DBT_SCHEMA", "dbt_budget")


# ─────────────────────────────────────────────
# Backend helpers
# ─────────────────────────────────────────────

def fetch_expenses_for_edit(
    date_from: date,
    date_to: date,
    category_filter: str,
    items_filter: str = "",
    id_filter: int | None = None,
    payment_filter: str = "All",
    amount_min: float | None = None,
    amount_max: float | None = None,
) -> pd.DataFrame:
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    try:
        cursor = conn.cursor()
        base_query = """
            SELECT
                e.id,
                e.date,
                e.items,
                e.amount,
                e.category,
                e.traveling_category,
                e.trip,
                e.payment_method,
                e.source_notes,
                e.amount_for_number_of_travelers,
                e.paid_for_number_of_travlerers,
                e.exclude_from_monthly,
                e.target_fund_category,
                e.split_fund_category_1,
                e.split_amount_1,
                -- Show linked transaction amounts for transparency
                COALESCE(
                    (SELECT SUM(ABS(t.amount))
                     FROM transactions t
                     WHERE t.expense_id = e.id), 0
                ) AS linked_transaction_total
            FROM expense e
            WHERE e.date BETWEEN %s AND %s
        """
        params = [date_from, date_to]
        if category_filter and category_filter != "All":
            base_query += " AND e.category = %s"
            params.append(category_filter)
        if items_filter:
            base_query += " AND e.items ILIKE %s"
            params.append(f"%{items_filter.strip()}%")
        if id_filter is not None:
            base_query += " AND e.id = %s"
            params.append(id_filter)
        if payment_filter and payment_filter != "All":
            base_query += " AND e.payment_method = %s"
            params.append(payment_filter)
        if amount_min is not None:
            base_query += " AND e.amount >= %s"
            params.append(amount_min)
        if amount_max is not None:
            base_query += " AND e.amount <= %s"
            params.append(amount_max)
        base_query += " ORDER BY e.date DESC, e.id DESC"
        cursor.execute(base_query, params)
        cols = [d[0] for d in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=cols)
    except psycopg2.Error as e:
        st.error(f"Error fetching expenses: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()


def update_expense(
    expense_id: int,
    new_date: date,
    new_items: str,
    new_amount: float,
    new_category: str,
    new_traveling_category: str | None,
    new_trip: str | None,
    new_payment_method: str,
    source_notes: str,
    amount_for_number_of_travelers: int | None,
    paid_for_number_of_travlerers: int | None,
    exclude_from_monthly: bool,
    target_fund_category: str | None,
    split_fund_category_1: str | None,
    split_amount_1: float,
) -> bool:
    """Update all editor fields and reconcile linked fund withdrawals atomically."""
    if not new_items.strip():
        st.error("Items cannot be empty.")
        return False
    if exclude_from_monthly and not target_fund_category:
        st.error("Select a primary target fund when Fund Withdrawal Required is checked.")
        return False
    if split_fund_category_1 and split_amount_1 <= 0:
        st.error("Secondary fund amount must be greater than 0.")
        return False
    if not split_fund_category_1 and split_amount_1 > 0:
        st.error("Select a secondary fund for the secondary amount.")
        return False
    if split_amount_1 >= new_amount and split_fund_category_1:
        st.error("Secondary fund amount must be smaller than the expense amount.")
        return False

    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date, category, exclude_from_monthly
            FROM expense WHERE id = %s FOR UPDATE
            """,
            (expense_id,),
        )
        old_row = cursor.fetchone()
        if old_row is None:
            st.error(f"Expense #{expense_id} was not found.")
            conn.rollback()
            return False

        cursor.execute(
            """
            UPDATE expense
            SET date = %s, items = %s, amount = %s, category = %s,
                traveling_category = %s, trip = %s, payment_method = %s,
                source_notes = %s, amount_for_number_of_travelers = %s,
                paid_for_number_of_travlerers = %s, exclude_from_monthly = %s,
                target_fund_category = %s, split_fund_category_1 = %s,
                split_amount_1 = %s
            WHERE id = %s
            """,
            (
                new_date, new_items.strip(), new_amount, new_category,
                new_traveling_category, new_trip, new_payment_method,
                source_notes.strip() or None, amount_for_number_of_travelers,
                paid_for_number_of_travlerers, exclude_from_monthly,
                target_fund_category if exclude_from_monthly else None,
                split_fund_category_1 if exclude_from_monthly else None,
                split_amount_1 if exclude_from_monthly else 0.0,
                expense_id,
            ),
        )

        # Rebuild only this expense's generated withdrawals. This covers all
        # transitions: regular -> fund withdrawal, fund withdrawal -> regular,
        # fund changes, amount changes, and date changes.
        cursor.execute("DELETE FROM transactions WHERE expense_id = %s", (expense_id,))
        if exclude_from_monthly:
            secondary_amount = min(split_amount_1 if split_fund_category_1 else 0.0, new_amount)
            primary_amount = new_amount - secondary_amount
            if primary_amount > 0:
                cursor.execute(
                    """
                    INSERT INTO transactions
                        (date, account_name, transaction_type, amount,
                         fund_category, transaction_category, source_notes, expense_id, trip)
                    VALUES (%s, %s, 'Withdrawal', %s, %s, 'Spending', %s, %s, %s)
                    """,
                    (new_date, "Main Chequing", -primary_amount, target_fund_category,
                     source_notes.strip() or None, expense_id, new_trip),
                )
            if secondary_amount > 0 and split_fund_category_1:
                cursor.execute(
                    """
                    INSERT INTO transactions
                        (date, account_name, transaction_type, amount,
                         fund_category, transaction_category, source_notes, expense_id, trip)
                    VALUES (%s, %s, 'Withdrawal', %s, %s, 'Spending', %s, %s, %s)
                    """,
                    (new_date, "Main Chequing", -secondary_amount, split_fund_category_1,
                     source_notes.strip() or None, expense_id, new_trip),
                )
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error updating expense details: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_expense(expense_id: int) -> bool:
    """
    Delete expense. Linked transactions are auto-deleted via ON DELETE CASCADE
    on the expense_id foreign key in the transactions table.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expense WHERE id = %s", (expense_id,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error deleting expense: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def fetch_linked_transactions(expense_id: int) -> pd.DataFrame:
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT transaction_id, fund_category, amount, source_notes, date
            FROM transactions
            WHERE expense_id = %s
            ORDER BY transaction_id
            """,
            (expense_id,)
        )
        cols = [d[0] for d in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=cols)
    except psycopg2.Error as e:
        st.error(f"Error fetching linked transactions: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────

def expense_editor_page():
    st.markdown(
        "<h1 style='color: #e67e22; text-align: center;'>✏️ Expense Editor</h1>",
        unsafe_allow_html=True,
    )
    if notice := st.session_state.pop("expense_editor_update_notice", None):
        st.warning(notice)
    if success_message := st.session_state.pop("expense_editor_success", None):
        st.success(success_message)
    st.markdown(
        "<p style='text-align: center; color: gray;'>"
        "Edit amount, category, or delete expenses. "
        "Linked fund withdrawal transactions update automatically."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Filters ──────────────────────────────
    st.subheader("Search Expenses")
    col1, col2, col3 = st.columns(3)
    with col1:
        date_from = st.date_input(
            "From", value=date.today() - timedelta(days=90)
        )
    with col2:
        date_to = st.date_input("To", value=date.today())
    with col3:
        category_filter = st.selectbox(
            "Category",
            ["All"] + expense_category_options + ["House"],
        )

    col4, col5, col6, col7, col8 = st.columns([1, 2, 1, 1, 1])
    with col4:
        id_filter_text = st.text_input("Expense ID")
    with col5:
        items_filter = st.text_input("Items contains")
    with col6:
        payment_filter = st.selectbox("Payment Method", ["All"] + payment_method)
    with col7:
        amount_min = st.number_input("Min Amount", min_value=0.0, value=0.0, format="%.2f")
    with col8:
        amount_max = st.number_input("Max Amount", min_value=0.0, value=0.0, format="%.2f")

    if st.button("🔍 Search", type="primary"):
        id_filter = None
        if id_filter_text.strip():
            if not id_filter_text.strip().isdigit() or int(id_filter_text.strip()) <= 0:
                st.error("Expense ID must be a positive whole number.")
                st.stop()
            id_filter = int(id_filter_text.strip())
        st.session_state["expense_editor_df"] = fetch_expenses_for_edit(
            date_from,
            date_to,
            category_filter,
            items_filter=items_filter,
            id_filter=id_filter,
            payment_filter=payment_filter,
            amount_min=amount_min if amount_min > 0 else None,
            amount_max=amount_max if amount_max > 0 else None,
        )
        st.session_state["expense_editor_filters"] = {
            "date_from": date_from,
            "date_to": date_to,
            "category_filter": category_filter,
            "items_filter": items_filter,
            "id_filter": id_filter,
            "payment_filter": payment_filter,
            "amount_min": amount_min if amount_min > 0 else None,
            "amount_max": amount_max if amount_max > 0 else None,
        }

    if "expense_editor_df" not in st.session_state:
        st.info("Set filters above and click Search to load expenses.")
        return

    df = st.session_state["expense_editor_df"]

    if df.empty:
        st.warning("No expenses found for the selected filters.")
        return

    st.markdown(f"**{len(df)} expenses found**")
    st.markdown("---")

    # ── Display and edit each row ─────────────
    def refresh_editor_results():
        filters = st.session_state.get(
            "expense_editor_filters",
            {
                "date_from": date_from,
                "date_to": date_to,
                "category_filter": category_filter,
                "items_filter": items_filter,
                "id_filter": None,
                "payment_filter": payment_filter,
                "amount_min": amount_min if amount_min > 0 else None,
                "amount_max": amount_max if amount_max > 0 else None,
            },
        )
        st.session_state["expense_editor_df"] = fetch_expenses_for_edit(**filters)

    trips = fetch_all_trips()
    for _, row in df.iterrows():
        expense_id = int(row["id"])
        has_linked = row["linked_transaction_total"] > 0

        with st.expander(
            f"{'🔗 ' if has_linked else ''}"
            f"**#{expense_id}** | **{row['date']}** | {row['items']} | "
            f"**${row['amount']:.2f}** | {row['category']}"
            f"{'  ← has linked transactions' if has_linked else ''}",
            expanded=False,
        ):
            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.caption(f"Expense ID: {expense_id}")
                st.markdown("**Edit Expense**")
                new_date = st.date_input(
                    "Date", value=pd.to_datetime(row["date"]).date(), key=f"date_{expense_id}"
                )
                new_items = st.text_input(
                    "Items",
                    value=row["items"] or "",
                    key=f"items_{expense_id}",
                )
                new_amount = st.number_input(
                    "Amount ($)",
                    min_value=0.0,
                    value=float(row["amount"]),
                    format="%.2f",
                    key=f"amount_{expense_id}",
                )
                current_cat_idx = (
                    expense_category_options.index(row["category"])
                    if row["category"] in expense_category_options else 0
                )
                new_category = st.selectbox(
                    "Category", expense_category_options, index=current_cat_idx,
                    key=f"cat_{expense_id}",
                )
                current_payment = row["payment_method"] or payment_method[0]
                payment_index = (
                    payment_method.index(current_payment)
                    if current_payment in payment_method
                    else 0
                )
                new_payment_method = st.selectbox(
                    "Payment Method",
                    payment_method,
                    index=payment_index,
                    key=f"payment_{expense_id}",
                )
                new_notes = st.text_input(
                    "Source Notes (e.g. 'partial refund applied')",
                    value=row["source_notes"] or "",
                    key=f"notes_{expense_id}",
                )

                with st.expander("Traveling Section", expanded=new_category == "Traveling"):
                    travel_idx = ([None] + traveling_category_options).index(row["traveling_category"]) \
                        if row["traveling_category"] in traveling_category_options else 0
                    new_traveling_category = st.selectbox(
                        "Traveling Category", [None] + traveling_category_options,
                        index=travel_idx, key=f"travel_category_{expense_id}",
                    )
                    trip_options = [None] + sorted(set(trips + ([row["trip"]] if row["trip"] else [])))
                    trip_idx = trip_options.index(row["trip"]) if row["trip"] in trip_options else 0
                    new_trip = st.selectbox("Trip", trip_options, index=trip_idx, key=f"trip_{expense_id}")
                    amount_travelers = st.number_input(
                        "Amount of Travelers", min_value=1, value=int(row["amount_for_number_of_travelers"] or 1),
                        step=1, key=f"travelers_{expense_id}"
                    )
                    paid_travelers = st.number_input(
                        "Amount of Travelers I Paid", min_value=0, value=int(row["paid_for_number_of_travlerers"] or 0),
                        step=1, key=f"paid_travelers_{expense_id}"
                    )

                with st.expander("Fund Withdrawal Section", expanded=bool(row["exclude_from_monthly"])):
                    new_exclude = st.checkbox(
                        "Fund Withdrawal Required (exclude from monthly expense)",
                        value=bool(row["exclude_from_monthly"]), key=f"exclude_{expense_id}",
                    )
                    fund_options = [None] + fund_categories
                    target_idx = fund_options.index(row["target_fund_category"]) if row["target_fund_category"] in fund_options else 0
                    new_target_fund = st.selectbox(
                        "Primary Target Fund Category", fund_options, index=target_idx,
                        key=f"target_fund_{expense_id}",
                    )
                    split_idx = fund_options.index(row["split_fund_category_1"]) if row["split_fund_category_1"] in fund_options else 0
                    new_split_fund = st.selectbox(
                        "Secondary Target Fund Category", fund_options, index=split_idx,
                        key=f"split_fund_{expense_id}",
                    )
                    new_split_amount = st.number_input(
                        "Secondary Amount", min_value=0.0, value=float(row["split_amount_1"] or 0.0),
                        format="%.2f", key=f"split_amount_{expense_id}"
                    )

                if st.button("💾 Submit Update", key=f"submit_update_{expense_id}", type="primary"):
                    validation_errors = []
                    if new_category == "Traveling":
                        if not new_traveling_category:
                            validation_errors.append("Traveling expenses need a Traveling Category.")
                        if not new_trip:
                            validation_errors.append("Traveling expenses need a Trip.")
                        if not new_exclude:
                            validation_errors.append("Traveling expenses need Fund Withdrawal Required checked.")
                    if new_exclude and not new_target_fund:
                        validation_errors.append("Fund Withdrawal Required needs a primary target fund.")
                    if validation_errors:
                        for error in validation_errors:
                            st.error(error)
                    else:
                        is_traveling = new_category == "Traveling"
                        success = update_expense(
                            expense_id, new_date, new_items, new_amount, new_category,
                            new_traveling_category if is_traveling else None,
                            new_trip if is_traveling else None, new_payment_method, new_notes,
                            amount_travelers if is_traveling else None,
                            paid_travelers if is_traveling else None, new_exclude,
                            new_target_fund, new_split_fund, new_split_amount,
                        )
                        if success:
                            st.session_state["expense_editor_success"] = (
                                f"Expense #{expense_id} updated. Linked fund withdrawals reconciled."
                            )
                            old_fund_state = bool(row["exclude_from_monthly"])
                            if new_date != pd.to_datetime(row["date"]).date() or new_category != row["category"] or new_exclude != old_fund_state:
                                st.session_state["expense_editor_update_notice"] = (
                                    "Remember: rerun monthly calculation if your date or "
                                    "category/fund-withdrawal status changed."
                                )
                            st.success(f"✅ Expense #{expense_id} updated. Linked fund withdrawals reconciled.")
                            refresh_editor_results()
                            st.rerun()

            with col_right:
                # ── Linked transactions ───────
                if has_linked:
                    st.markdown("**Linked Fund Transactions**")
                    linked_df = fetch_linked_transactions(expense_id)
                    if not linked_df.empty:
                        for _, lt in linked_df.iterrows():
                            color = "#e74c3c" if lt["amount"] < 0 else "#2ecc71"
                            st.markdown(
                                f"<p style='color:{color}; font-size:14px;'>"
                                f"<b>{lt['fund_category']}</b>: ${lt['amount']:.2f}<br>"
                                f"<span style='color:gray;font-size:12px;'>{lt['source_notes'] or ''}</span>"
                                f"</p>",
                                unsafe_allow_html=True,
                            )
                else:
                    st.markdown(
                        "<p style='color: gray; font-size: 13px;'>No linked fund transactions.</p>",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

                # ── Delete ───────────────────
                st.markdown("**Delete Expense**")
                if has_linked:
                    st.warning(
                        f"⚠️ This will also delete "
                        f"{int(row['linked_transaction_total'] > 0)} linked transaction(s)."
                    )

                confirm_key = f"confirm_delete_{expense_id}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_btn_{expense_id}",
                        type="secondary",
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    st.error("Are you sure? This cannot be undone.")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button(
                            "✅ Yes, Delete",
                            key=f"confirm_yes_{expense_id}",
                        ):
                            success = delete_expense(expense_id)
                            if success:
                                st.success(f"Expense #{expense_id} deleted.")
                                st.session_state[confirm_key] = False
                                refresh_editor_results()
                                st.rerun()
                    with col_no:
                        if st.button(
                            "❌ Cancel",
                            key=f"confirm_no_{expense_id}",
                        ):
                            st.session_state[confirm_key] = False
                            st.rerun()


if __name__ == "__main__":
    expense_editor_page()
