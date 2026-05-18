import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data, fetch_expense_withdrawal_transactions
from utils.data import years
from modules.current_saving.component.Pivot_Table import Pivot_Table
from modules.current_saving.component.Account_Sum import Account_Sum
from modules.current_saving.component.Saving_Sum import saving_sum
st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def current_saving_status():
    today_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    st.markdown(f"<h1 style='color: #ffffff; text-align: center;'>Fund Distribution by Account and Category - {today_date} </h1>", unsafe_allow_html=True)
    columns_names, all_transaction_data = fetch_all_transaction_data()
    transaction_data = pd.DataFrame(all_transaction_data, columns=columns_names)

    Account_Sum(transaction_data)

    Pivot_Table(transaction_data)

    st.write("___")

    saving_sum(transaction_data)

    # --- Auto Fund Withdrawals from Expenses ---
    st.write("___")
    st.markdown("<h3 style='color: #ff9900; text-align: center;'>⚡ Auto Fund Withdrawals from Expenses</h3>", unsafe_allow_html=True)
    st.info(
        "These are the withdrawal transactions automatically created by the database trigger when an expense with a "
        "Target Fund Category is saved. This table reflects all expense-linked fund deductions, including prepaid ones."
    )
    expense_withdrawals = fetch_expense_withdrawal_transactions()
    if not expense_withdrawals.empty:
        # Summary by fund_category
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4 style='color: #f1c40f;'>Withdrawal Summary by Fund</h4>", unsafe_allow_html=True)
            summary = (
                expense_withdrawals.groupby(['fund_category', 'transaction_type'])['amount']
                .sum()
                .reset_index()
                .rename(columns={'amount': 'Total Amount', 'fund_category': 'Fund Category', 'transaction_type': 'Type'})
            )
            st.dataframe(summary, hide_index=True, use_container_width=True)
        with col2:
            st.markdown("<h4 style='color: #f1c40f;'>Recent Expense-Linked Transactions</h4>", unsafe_allow_html=True)
            display_cols = ['date', 'amount', 'fund_category', 'transaction_type', 'prepaid', 'expense_items', 'trip']
            available_cols = [c for c in display_cols if c in expense_withdrawals.columns]
            st.dataframe(expense_withdrawals[available_cols].head(20), hide_index=True, use_container_width=True)
    else:
        st.info("No expense-linked transactions found yet. Save an expense with a Target Fund Category to see data here.")

if __name__ == "__main__":
    current_saving_status()