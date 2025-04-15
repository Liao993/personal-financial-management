import streamlit as st # type: ignore
import pandas as pd

if 'recorded_transactions' not in st.session_state:
    st.session_state['recorded_transactions'] = []

def record_saving_transaction(transaction_date, account_name, action_type, amount, fund_category=None, source_notes=None, transfer_to_account=None):
    st.subheader("Review Recorded Transaction")

    transaction = {
        "Date": transaction_date,
        "Account": account_name,
        "Type": action_type,
        "Amount": amount,
        "Category": fund_category,
        "Notes": source_notes,
        "Transfer To": transfer_to_account
    }
    st.session_state['recorded_transactions'].append(transaction)
    

def display_recorded_transactions():
    if st.session_state['recorded_transactions']:
        st.subheader("Recorded Transactions")
        df = pd.DataFrame(st.session_state['recorded_transactions'])
        st.dataframe(df)
    else:
        st.info("No transactions recorded yet.")