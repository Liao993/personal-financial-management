import streamlit as st # type: ignore
from modules.transaction.transaction_form import transaction_form
from modules.transaction.fund_transfer_form import fund_transfer_form
from modules.transaction.transaction_review import display_recorded_transactions
from modules.transaction.transaction_saving import transaction_savings_action
from backend.transaction_backend import fetch_last_transaction_data

st.set_page_config(page_title="Account Transfers", page_icon="🔁", layout="wide")


def reset_transaction_page_state():
    st.session_state["show_the_form"] = True
    st.session_state["recorded_transactions"] = []
    st.session_state["transfer_mode"] = "Account Transfer"
    st.session_state["transaction_form_version"] = (
        st.session_state.get("transaction_form_version", 0) + 1
    )


def transaction_actions_page():
    st.markdown("<h1 style='text-align: center; color: #16a085'>Transfers</h1>", unsafe_allow_html=True)

    transfer_mode = st.radio(
        "Transfer Type",
        ["Account Transfer", "Fund Transfer"],
        index=0,
        horizontal=True,
        key="transfer_mode",
        help=(
            "Account Transfer moves money between accounts in one fund. "
            "Fund Transfer moves money between funds in one account."
        ),
    )

    if 'show_the_form' not in st.session_state:
        st.session_state['show_the_form'] = True

    if 'recorded_transactions' not in st.session_state:
        st.session_state['recorded_transactions'] = []

    if st.session_state.pop("transaction_success_message", None):
        st.success("Transaction recorded successfully.")

    if st.session_state['show_the_form']:
        if transfer_mode == "Account Transfer":
            st.caption("Move money between accounts within the same fund category.")
            transaction_form()
        else:
            st.caption("Move money between funds while keeping the account fixed.")
            fund_transfer_form()
        st.write("---")
        # Print out the last transaction data
        last_transaction_data = fetch_last_transaction_data()
        if not last_transaction_data.empty:
            st.write("Last Transaction Data:")
            st.table(last_transaction_data)

    else:
        
        data = display_recorded_transactions()
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.button("Submit Transactions")
            if submitted:
                success = transaction_savings_action(data)
                if success:
                    st.session_state["transaction_success_message"] = True
                    reset_transaction_page_state()
                    st.rerun()
                else:
                    st.error("Failed to record transaction. Please check the data.")
                    reset_transaction_page_state()
                    st.rerun()
        with col2:
            edit_button = st.button("Edit Transactions")
            if edit_button:
                reset_transaction_page_state()
                st.rerun()
    
if __name__ == "__main__":
    transaction_actions_page()
