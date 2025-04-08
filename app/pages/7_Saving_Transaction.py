import streamlit as st # type: ignore
from datetime import datetime
from utils.css import drop_down_list

def record_saving_transaction(transaction_date, account_name, transaction_type, amount, fund_category=None, source_notes=None, transfer_to_account=None):
  
    st.write(f"Recording Transaction:")
    st.write(f"  Date: {transaction_date}")
    st.write(f"  Account: {account_name}")
    st.write(f"  Type: {transaction_type}")
    st.write(f"  Amount: {amount}")
    if fund_category:
        st.write(f"  Fund Category: {fund_category}")
    if source_notes:
        st.write(f"  Notes: {source_notes}")
    if transfer_to_account:
        st.write(f"  Transfer To: {transfer_to_account}")
    st.success("Transaction recorded (placeholder).")

def saving_actions_page():
    st.title("Saving Actions")

    drop_down_list()

    action_type = st.radio(
        "What type of action would you like to record?",
        ["Deposit", "Withdrawal", "Transfer"]
    )
   
    transaction_date = st.date_input("Transaction Date", datetime.now().date())

    fund_categories = ["Traveling funds", "Retirement Saving", "Medium-term Saving", "Direct Investing", "other"]
    fund_category = st.selectbox("Fund Category", fund_categories)

    account_name = st.selectbox("Account", ["RBC Chequing", "Questrade TFSA", "Questrade RRSP", "Moomoo TFSA", "RBC TFSA"])
    amount = st.number_input("Amount", min_value=0.00)
    source_notes = st.text_input("Notes (Optional)")
   
    fund_category = None
    transfer_to_account = None

    if action_type == "Deposit":
        if st.button("Record Deposit"):
            record_saving_transaction(transaction_date, account_name, "Deposit", amount, fund_category, source_notes)

    elif action_type == "Withdrawal":
        if st.button("Record Withdrawal"):
            record_saving_transaction(transaction_date, account_name, "Withdrawal", -amount, fund_category, source_notes)

    elif action_type == "Transfer":
        transfer_to_account = st.selectbox("Transfer To Account", ["A", "B", "C", "D", "E"], index=1) # Default to a different account
        if st.button("Record Transfer"):
            # For a transfer, we'll record two transactions: one out, one in
            record_saving_transaction(transaction_date, account_name, "Transfer_out", -amount, source_notes=f"Transfer to {transfer_to_account} - {source_notes}", transfer_to_account=transfer_to_account)
            record_saving_transaction(transaction_date, transfer_to_account, "Transfer_into", amount, source_notes=f"Transfer from {account_name} - {source_notes}")

if __name__ == "__main__":
    saving_actions_page()