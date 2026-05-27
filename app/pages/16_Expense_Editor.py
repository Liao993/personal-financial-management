import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from datetime import date, timedelta
from utils.connection import get_db_connection
import psycopg2  # type: ignore
import os

st.set_page_config(page_title="Expense Editor", page_icon="✏️", layout="wide")

DBT_SCHEMA = os.environ.get("DBT_SCHEMA", "dbt_budget")


# ─────────────────────────────────────────────
# Backend helpers
# ─────────────────────────────────────────────

def fetch_expenses_for_edit(date_from: date, date_to: date, category_filter: str) -> pd.DataFrame:
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


def update_expense_amount(expense_id: int, new_amount: float, source_notes: str) -> bool:
    """Update expense amount and notes. Trigger handles transaction sync automatically."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE expense
            SET amount = %s, source_notes = %s
            WHERE id = %s
            """,
            (new_amount, source_notes, expense_id)
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error updating expense: {e}")
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
            ["All", "Grocery", "Food Outside", "Household Goods", "Cell Phone",
             "Gas", "Donation", "Gifts", "Medicine", "Exercise", "Saved For Love",
             "Transportation", "Education", "Traveling", "Fun/Tickets", "Clothing",
             "Liquor", "Others", "Car", "House"],
        )

    if st.button("🔍 Search", type="primary"):
        st.session_state["expense_editor_df"] = fetch_expenses_for_edit(
            date_from, date_to, category_filter
        )

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
    from utils.data import expense_category_options

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
                # ── Amount edit ──────────────
                st.markdown("**Edit Amount & Notes**")
                new_amount = st.number_input(
                    "Amount ($)",
                    min_value=0.0,
                    value=float(row["amount"]),
                    format="%.2f",
                    key=f"amount_{expense_id}",
                )
                new_notes = st.text_input(
                    "Source Notes (e.g. 'partial refund applied')",
                    value=row["source_notes"] or "",
                    key=f"notes_{expense_id}",
                )

                if st.button(
                    "💾 Save Amount & Notes",
                    key=f"save_amount_{expense_id}",
                ):
                    if new_amount != float(row["amount"]) or new_notes != (row["source_notes"] or ""):
                        success = update_expense_amount(expense_id, new_amount, new_notes)
                        if success:
                            st.success(
                                f"✅ Expense #{expense_id} updated to ${new_amount:.2f}."
                                + (" Linked transactions synced automatically." if has_linked else "")
                            )
                            # Refresh
                            st.session_state["expense_editor_df"] = fetch_expenses_for_edit(
                                date_from, date_to, category_filter
                            )
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
                            st.session_state["expense_editor_df"] = fetch_expenses_for_edit(
                                date_from, date_to, category_filter
                            )
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
                                st.session_state["expense_editor_df"] = fetch_expenses_for_edit(
                                    date_from, date_to, category_filter
                                )
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
