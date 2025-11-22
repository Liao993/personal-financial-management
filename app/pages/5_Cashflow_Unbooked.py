import streamlit as st # type: ignore
from modules.cashflow_unbooked.transaction_form import transaction_form
from modules.cashflow_unbooked.transaction_review import display_recorded_transactions
from modules.cashflow_unbooked.transaction_saving import transaction_savings_action
from backend.cashflow_backend import fetch_last_cashflow_data, fetch_transaction_data_by_account_by_month
import time

st.set_page_config(page_title="Transaction", page_icon="💰", layout="wide")


def unbooked_transaction_actions_page():
    st.markdown("<h1 style='text-align: center; color: #a0c4ff'>Unbooked Transaction</h1>", unsafe_allow_html=True)

    if 'show_the_form' not in st.session_state:
        st.session_state['show_the_form'] = True

    if 'recorded_transactions' not in st.session_state:
        st.session_state['recorded_transactions'] = []

    if st.session_state['show_the_form']:
        st.subheader("Unbooked Cashflow Summary")
        # Print out the last transaction data
        last_cashflow_summary = fetch_transaction_data_by_account_by_month()
        if not last_cashflow_summary.empty:
            st.info("The table shows how to move money for expenses payments.")
            last_cashflow_summary.rename(columns={'total_amount': 'total_amount_left'}, inplace=True)
            st.dataframe(last_cashflow_summary, hide_index=True)
        st.write("---")
        transaction_form()
        st.write("---")
        # Print out the last transaction data
        last_cashflow_data = fetch_last_cashflow_data()
        if not last_cashflow_data.empty:
            st.write("Last Cashflow Data:")
            st.table(last_cashflow_data)
        
        

    else:
        
        data = display_recorded_transactions()
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.button("Submit Transactions")
            if submitted:
                success = transaction_savings_action(data)
                if success:
                    st.success("Transaction recorded successfully!")
                    time.sleep(2)
                    st.session_state['show_the_form'] = True
                    st.session_state['recorded_transactions'] = []
                    st.rerun()
                else:
                    st.error("Failed to record transaction. Please check the data.")
                    time.sleep(20)
                    st.session_state['show_the_form'] = True
                    st.session_state['recorded_transactions'] = []
                    st.rerun()
        with col2:
            edit_button = st.button("Edit Transactions")
            if edit_button:
                st.session_state['show_the_form'] = True
                st.session_state['recorded_transactions'] = []
                st.rerun()
    
if __name__ == "__main__":
    unbooked_transaction_actions_page() # Call the function to display the page content when the script is run directly