import streamlit as st # type: ignore
from datetime import datetime
from utils.css import drop_down_list
from utils.data import account_name_list, usable_fund_categories, transaction_type_list
from  modules.transaction.transaction_review import record_saving_transaction

def transaction_form():
    st.subheader("Record New Transaction")

    drop_down_list()

    st.write("If money balance BETWEEN DIFFERENT FUNDS, choose deposit or withdraw, if it is the same funds but in different accounts, choose transfer between accounts.")
    st.write("For example, From Medium-term Saving to Traveling Funds, please make 'TWO' transactions. choose Withdrawl for Medium-term and Deposit for Traveling Funds")
    action_type = st.radio(
        "What type of action would you like to record?",
        transaction_type_list,
         key="action_type_form"
    )
    transaction_date = st.date_input("Transaction Date", datetime.now().date())
    fund_category = st.selectbox("Usable Fund Category", usable_fund_categories)
    account_name = st.selectbox("Account", account_name_list)
    amount = st.number_input("Amount", min_value=0.0)
    source_notes = st.text_input("Notes (Optional)")

    transfer_to_account = None

    if action_type == "Deposit (between funds or savings)":
        if st.button("Record Deposit"):
            record_saving_transaction(transaction_date, account_name, "Deposit", amount, fund_category, source_notes)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()

    elif action_type == "Withdrawal (between funds or spending)":
        if st.button("Record Withdrawal"):
            record_saving_transaction(transaction_date, account_name, "Withdrawal", -amount, fund_category, source_notes)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()

    
    elif action_type == "Transfer Between Accounts":
        transfer_to_account = st.selectbox("Transfer To Account (Different Accounts)", account_name_list, index=1) # Default to a different account
        if st.button("Record Transfer"):
            # For a transfer, we'll record two transactions: one out, one in
            record_saving_transaction(transaction_date, account_name, "Transfer Out", -amount, fund_category, source_notes=f"Transfer to {transfer_to_account} {source_notes}", transfer_to_account=transfer_to_account)
            record_saving_transaction(transaction_date, transfer_to_account, "Transfer In", amount, fund_category, source_notes=f"Transfer from {account_name} {source_notes}")
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()