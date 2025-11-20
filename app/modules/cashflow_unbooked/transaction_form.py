import streamlit as st # type: ignore
from datetime import datetime
from utils.css import drop_down_list
from utils.data import account_name_list, cashflow_transaction_type_list, cashflow_purpose
from modules.cashflow_unbooked.transaction_review import record_saving_transaction
from modules.cashflow_unbooked.transaction_instruction import instruction
def transaction_form():
    st.subheader("Record New Cashflow Transaction")

    drop_down_list()

    instruction()

    st.markdown(f"<p style='font-size: 24px; color: #a0c4ff;'><b>Please choose the action type and fill the form below:</b></p>", unsafe_allow_html=True)
    action_type = st.radio(
        "",
        cashflow_transaction_type_list,
        key="action_type_form"
    )
    transaction_date = st.date_input("Transaction Date", datetime.now().date())
    account_name = st.selectbox("Account", account_name_list)
    amount = st.number_input("Amount", min_value=0.0)
    purpose = st.selectbox("Purpose", cashflow_purpose)
    source_notes = st.text_input("Notes (Optional)")
    transfer_to_account = None

    if action_type == "Deposit (Income)":
        if st.button("Record Deposit"):
            record_saving_transaction(transaction_date, account_name, "Deposit", amount, purpose, source_notes)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()

    elif action_type == "Withdrawal (Daily and House Expenses)":
        if st.button("Record Withdrawal"):
            record_saving_transaction(transaction_date, account_name, "Withdrawal", -amount, purpose, source_notes)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()

    
    elif action_type == "Transfer Between Accounts":
        transfer_to_account = st.selectbox("Transfer To Account (Different Accounts)", account_name_list, index=2) # Default to a different account
        if st.button("Record Transfer"):
            # For a transfer, we'll record two transactions: one out, one in
            record_saving_transaction(transaction_date, account_name, "Transfer Out", -amount, purpose, source_notes=f"Transfer to {transfer_to_account} {source_notes}", transfer_to_account=transfer_to_account)
            record_saving_transaction(transaction_date, transfer_to_account, "Transfer In", amount, purpose, source_notes=f"Transfer from {account_name} {source_notes}")
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()