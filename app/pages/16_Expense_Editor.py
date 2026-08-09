from __future__ import annotations

import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from datetime import date, timedelta
from utils.connection import get_db_connection
import psycopg2  # type: ignore
import os
from utils.data import expense_category_options, payment_method

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
                e.payment_method,
                e.source_notes,
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


def update_expense_details(
    expense_id: int,
    new_items: str,
    new_amount: float,
    new_payment_method: str,
    source_notes: str,
) -> bool:
    """Update editable details. Trigger handles transaction sync when amount changes."""
    if not new_items.strip():
        st.error("Items cannot be empty.")
        return False

    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE expense
            SET items = %s,
                amount = %s,
                payment_method = %s,
                source_notes = %s
            WHERE id = %s
            """,
            (new_items.strip(), new_amount, new_payment_method, source_notes, expense_id)
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


def update_expense_category(expense_id: int, new_category: str) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE expense SET category = %s WHERE id = %s",
            (new_category, expense_id)
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error updating category: {e}")
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

    col4, col5, col6, col7 = st.columns([2, 1, 1, 1])
    with col4:
        items_filter = st.text_input("Items contains")
    with col5:
        payment_filter = st.selectbox("Payment Method", ["All"] + payment_method)
    with col6:
        amount_min = st.number_input("Min Amount", min_value=0.0, value=0.0, format="%.2f")
    with col7:
        amount_max = st.number_input("Max Amount", min_value=0.0, value=0.0, format="%.2f")

    if st.button("🔍 Search", type="primary"):
        st.session_state["expense_editor_df"] = fetch_expenses_for_edit(
            date_from,
            date_to,
            category_filter,
            items_filter=items_filter,
            payment_filter=payment_filter,
            amount_min=amount_min if amount_min > 0 else None,
            amount_max=amount_max if amount_max > 0 else None,
        )
        st.session_state["expense_editor_filters"] = {
            "date_from": date_from,
            "date_to": date_to,
            "category_filter": category_filter,
            "items_filter": items_filter,
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
                "payment_filter": payment_filter,
                "amount_min": amount_min if amount_min > 0 else None,
                "amount_max": amount_max if amount_max > 0 else None,
            },
        )
        st.session_state["expense_editor_df"] = fetch_expenses_for_edit(**filters)

    for _, row in df.iterrows():
        expense_id = int(row["id"])
        has_linked = row["linked_transaction_total"] > 0

        with st.expander(
            f"{'🔗 ' if has_linked else ''}"
            f"**{row['date']}** | {row['items']} | "
            f"**${row['amount']:.2f}** | {row['category']}"
            f"{'  ← has linked transactions' if has_linked else ''}",
            expanded=False,
        ):
            col_left, col_right = st.columns([2, 1])

            with col_left:
                # ── Details edit ─────────────
                st.markdown("**Edit Details**")
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

                if st.button(
                    "💾 Save Details",
                    key=f"save_details_{expense_id}",
                ):
                    changed = (
                        new_items != (row["items"] or "")
                        or new_amount != float(row["amount"])
                        or new_payment_method != (row["payment_method"] or "")
                        or new_notes != (row["source_notes"] or "")
                    )
                    if changed:
                        success = update_expense_details(
                            expense_id,
                            new_items,
                            new_amount,
                            new_payment_method,
                            new_notes,
                        )
                        if success:
                            st.success(
                                f"✅ Expense #{expense_id} details updated."
                                + (" Linked transactions synced automatically." if has_linked else "")
                            )
                            refresh_editor_results()
                            st.rerun()
                    else:
                        st.info("No changes detected.")

                st.markdown("---")

                # ── Category edit ────────────
                st.markdown("**Edit Category**")
                current_cat_idx = (
                    expense_category_options.index(row["category"])
                    if row["category"] in expense_category_options
                    else 0
                )
                new_category = st.selectbox(
                    "Category",
                    expense_category_options,
                    index=current_cat_idx,
                    key=f"cat_{expense_id}",
                )
                if st.button(
                    "💾 Save Category",
                    key=f"save_cat_{expense_id}",
                ):
                    if new_category != row["category"]:
                        success = update_expense_category(expense_id, new_category)
                        if success:
                            st.success(f"✅ Category updated to {new_category}.")
                            refresh_editor_results()
                            st.rerun()
                    else:
                        st.info("Category unchanged.")

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
