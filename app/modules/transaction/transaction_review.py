import streamlit as st # type: ignore
import pandas as pd



def record_saving_transaction(transaction_date, account_name, action_type, amount, fund_category=None, source_notes=None, transfer_to_account=None, transfer_to_fund=None):
    st.subheader("Review Recorded Transaction")

    transaction = {
        "Transaction Date": transaction_date,
        "Account Name": account_name,
        "Usable Fund Category": fund_category,
        "Transaction Type": action_type,
        "Amount": amount,
        "Notes": source_notes,
        "Transfer To Account": transfer_to_account,
        "Transfer To Fund": transfer_to_fund
    }
    st.session_state['recorded_transactions'].append(transaction)
    

def display_recorded_transactions():
    if st.session_state['recorded_transactions']:
        st.subheader("Recorded Transactions")
        df = pd.DataFrame(st.session_state['recorded_transactions'])
        st.dataframe(df)
    else:
        st.info("No transactions recorded yet.")