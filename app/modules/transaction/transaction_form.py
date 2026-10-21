import streamlit as st  # type: ignore
from datetime import datetime
from utils.css import drop_down_list
from utils.data import account_name_list, fund_categories, transaction_type_list
from modules.transaction.transaction_review import record_saving_transaction
from modules.transaction.transaction_instruction import instruction


def transaction_form():
    form_version = st.session_state.get("transaction_form_version", 0)
    st.subheader(
        "Record New Transaction: Track all money flow between accounts."
    )

    drop_down_list()
    instruction()

    st.markdown(
        "<p style='font-size: 24px; color: #16a085;'>"
        "<b>Please choose the action type and fill the form below:</b></p>",
        unsafe_allow_html=True,
    )

    action_type = st.radio(
        "",
        transaction_type_list,
        key=f"action_type_form_{form_version}",
    )

    transaction_date  = st.date_input(
        "Transaction Date", datetime.now().date(), key=f"transaction_date_{form_version}"
    )
    fund_category     = st.selectbox(
        "Usable Fund Category", fund_categories, key=f"fund_category_{form_version}"
    )
    account_name      = st.selectbox(
        "Account", account_name_list, key=f"account_name_{form_version}"
    )
    amount            = st.number_input(
        "Amount", min_value=0.0, key=f"transaction_amount_{form_version}"
    )
    source_notes      = st.text_input("Notes (Optional)", key=f"transaction_notes_{form_version}")
    transfer_to_account = None

    if action_type == "Deposit (between funds or savings)":
        if st.button("Record Deposit"):
            record_saving_transaction(
                transaction_date, account_name, "Deposit",
                amount, fund_category, source_notes,
            )
            st.session_state["show_the_form"] = False
            st.rerun()

    elif action_type == "Withdrawal (between funds or spending)":
        if st.button("Record Withdrawal"):
            record_saving_transaction(
                transaction_date, account_name, "Withdrawal",
                -amount, fund_category, source_notes,
            )
            st.session_state["show_the_form"] = False
            st.rerun()

    elif action_type == "Transfer Between Accounts":
        transfer_to_account = st.selectbox(
            "Transfer To Account (Different Accounts)",
            account_name_list,
            index=2,
            key=f"transfer_to_account_{form_version}",
        )
        if st.button("Record Transfer"):
            record_saving_transaction(
                transaction_date, account_name, "Transfer Out",
                -amount, fund_category,
                source_notes=f"Transfer to {transfer_to_account} {source_notes}",
                transfer_to_account=transfer_to_account,
            )
            record_saving_transaction(
                transaction_date, transfer_to_account, "Transfer In",
                amount, fund_category,
                source_notes=f"Transfer from {account_name} {source_notes}",
            )
            st.session_state["show_the_form"] = False
            st.rerun()
