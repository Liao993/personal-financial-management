import streamlit as st # type: ignore
import pandas as pd # type: ignore



def record_saving_transaction(transaction_date, account_name, action_type, amount, fund_category=None, source_notes=None, transfer_to_account=None, prepaid=False):
    st.subheader("Review Recorded Transaction")

    transaction = {
        "Transaction Date": transaction_date,
        "Account Name": account_name,
        "Usable Fund Category": fund_category,
        "Transaction Type": action_type,
        "Amount": amount,
        "Notes": source_notes,
        "Transfer To Account": transfer_to_account,
        "Prepaid": prepaid
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