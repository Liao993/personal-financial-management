import streamlit as st # type: ignore
import pandas as pd # type: ignore



def record_saving_transaction(transaction_date, account_name, action_type, amount, purpose=None, source_notes=None, transfer_to_account=None):
    st.subheader("Review Your Recorded Transaction:")

    transaction = {
        "Transaction Date": transaction_date,
        "Account Name": account_name,
        "Transaction Type": action_type,
        "Amount": amount,
        "Purpose": purpose,
        "Notes": source_notes,
        "Transfer To Account": transfer_to_account
    }
    st.session_state['recorded_transactions'].append(transaction)
    

def display_recorded_transactions():
    if st.session_state['recorded_transactions']:
        st.subheader("Recorded Transactions")
        df = pd.DataFrame(st.session_state['recorded_transactions'])
        st.dataframe(df)
        return st.session_state['recorded_transactions']
    else:
        st.info("No transactions recorded yet.")

def display_recorded_transactions_income_page():
    if st.session_state['recorded_transactions']:
        df = pd.DataFrame(st.session_state['recorded_transactions'])
        st.dataframe(df)
        return st.session_state['recorded_transactions']
    else:
        st.info("No transactions recorded yet.")