import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from backend.transaction_backend import (
    fetch_all_transaction_data,
    fetch_expense_withdrawal_transactions,
)
from utils.data import years
from modules.current_saving.component.Pivot_Table import Pivot_Table
from modules.current_saving.component.Account_Sum import Account_Sum
from modules.current_saving.component.Saving_Sum import saving_sum

st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def add_expense_withdrawals_to_transactions(
    transaction_data: pd.DataFrame,
    expense_withdrawals: pd.DataFrame,
) -> pd.DataFrame:
    if expense_withdrawals.empty:
        return transaction_data

    expense_txn_for_sum = expense_withdrawals[
        ["date", "account_name", "amount", "fund_category", "transaction_type"]
    ].copy()

    return pd.concat(
        [transaction_data, expense_txn_for_sum],
        ignore_index=True,
    )


def current_saving_status():
    today_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    st.markdown(
        f"<h1 style='color: #ffffff; text-align: center;'>"
        f"Fund Distribution by Account and Category - {today_date}"
        f"</h1>",
        unsafe_allow_html=True,
    )

    columns_names, all_transaction_data = fetch_all_transaction_data()
    transaction_data = pd.DataFrame(all_transaction_data, columns=columns_names)
    expense_withdrawals_raw = fetch_expense_withdrawal_transactions()
    transaction_data_with_withdrawals = add_expense_withdrawals_to_transactions(
        transaction_data,
        expense_withdrawals_raw,
    )

    Account_Sum(transaction_data_with_withdrawals)
    Pivot_Table(transaction_data_with_withdrawals)

    st.write("___")
    # Include expense-linked withdrawals so saving_sum reflects fund deductions
    # (fetch_all_transaction_data only returns expense_id IS NULL rows)
    saving_sum(transaction_data_with_withdrawals)

    

if __name__ == "__main__":
    current_saving_status()
