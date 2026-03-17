import streamlit as st # type: ignore
from datetime import datetime
from utils.css import drop_down_list
from utils.data import account_name_list, fund_categories, transaction_type_list
from modules.transaction.transaction_review import record_saving_transaction
from modules.transaction.transaction_instruction import instruction
def transaction_form():
    st.subheader("Record New Transaction")

    drop_down_list()

    instruction()

    st.markdown(f"<p style='font-size: 24px; color: #16a085;'><b>Please choose the action type and fill the form below:</b></p>", unsafe_allow_html=True)
    action_type = st.radio(
        "",
        transaction_type_list,
        key="action_type_form"
    )
    transaction_date = st.date_input("Transaction Date", datetime.now().date())
    fund_category = st.selectbox("Usable Fund Category", fund_categories)
    account_name = st.selectbox("Account", account_name_list)
    amount = st.number_input("Amount", min_value=0.0)
    prepaid = st.checkbox("Prepaid (Check it if the spending is paid in advance and got the money later (Both for Withdrawl and Deposit)).")
    source_notes = st.text_input("Notes (Optional)")
    transfer_to_account = None

    if action_type == "Deposit (between funds or savings)":
        if st.button("Record Deposit"):
            record_saving_transaction(transaction_date, account_name, "Deposit", amount, fund_category, source_notes, prepaid)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()

    elif action_type == "Withdrawal (between funds or spending)":
        if st.button("Record Withdrawal"):
            record_saving_transaction(transaction_date, account_name, "Withdrawal", -amount, fund_category, source_notes, prepaid)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()

    
    elif action_type == "Transfer Between Accounts":
        transfer_to_account = st.selectbox("Transfer To Account (Different Accounts)", account_name_list, index=2) # Default to a different account
        if st.button("Record Transfer"):
            # For a transfer, we'll record two transactions: one out, one in
            record_saving_transaction(transaction_date, account_name, "Transfer Out", -amount, fund_category, source_notes=f"Transfer to {transfer_to_account} {source_notes}", transfer_to_account=transfer_to_account, prepaid=prepaid)
            record_saving_transaction(transaction_date, transfer_to_account, "Transfer In", amount, fund_category, source_notes=f"Transfer from {account_name} {source_notes}", prepaid=prepaid)
            st.session_state['show_the_form'] = False # Set session state
            st.rerun()