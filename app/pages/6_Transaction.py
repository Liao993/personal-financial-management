import streamlit as st # type: ignore
from modules.transaction.transaction_form import transaction_form
from modules.transaction.transaction_review import display_recorded_transactions
from modules.transaction.transaction_saving import transaction_savings_action
import time

st.set_page_config(page_title="Transaction", page_icon="💰", layout="wide")


def transaction_actions_page():
    st.markdown("<h1 style='text-align: center;'>Transaction</h1>", unsafe_allow_html=True)

    if 'show_the_form' not in st.session_state:
        st.session_state['show_the_form'] = True

    if 'recorded_transactions' not in st.session_state:
        st.session_state['recorded_transactions'] = []

    if st.session_state['show_the_form']:

        transaction_form()
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
    transaction_actions_page()