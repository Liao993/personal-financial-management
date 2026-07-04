import streamlit as st  # type: ignore
from datetime import datetime
from pydantic import ValidationError  # type: ignore

from utils.data import account_name_list, fund_categories, transaction_type_list
from backend.transaction_backend import insert_transaction_data
from models.transaction_models import Transaction


def render_transaction_section():
    st.subheader("🔁 Quick Transaction")

    action_type = st.radio("Action", transaction_type_list, key="mobile_action_type")

    with st.form("mobile_transaction_form"):
        transaction_date = st.date_input(
            "Date", value=datetime.now().date(), key="mobile_transaction_date"
        )
        fund_category = st.selectbox(
            "Fund Category", fund_categories, key="mobile_fund_category"
        )
        account_name = st.selectbox("Account", account_name_list, key="mobile_account_name")
        amount = st.number_input("Amount", min_value=0.0, key="mobile_transaction_amount")
        source_notes = st.text_input("Notes (optional)", "", key="mobile_transaction_notes")

        transfer_to_account = None
        if action_type == "Transfer Between Accounts":
            transfer_to_account = st.selectbox(
                "Transfer To Account",
                account_name_list,
                index=min(2, len(account_name_list) - 1),
                key="mobile_transfer_to_account",
            )

        submitted = st.form_submit_button("Save Transaction")

    if submitted:
        try:
            if action_type == "Deposit (between funds or savings)":
                txn = Transaction(
                    date=transaction_date,
                    account_name=account_name,
                    transaction_type="Deposit",
                    amount=amount,
                    fund_category=fund_category,
                    source_notes=source_notes,
                )
                insert_transaction_data(txn.dict())
                st.success(f"✅ Deposit of ${amount:.2f} saved.")

            elif action_type == "Withdrawal (between funds or spending)":
                txn = Transaction(
                    date=transaction_date,
                    account_name=account_name,
                    transaction_type="Withdrawal",
                    amount=-amount,
                    fund_category=fund_category,
                    source_notes=source_notes,
                )
                insert_transaction_data(txn.dict())
                st.success(f"✅ Withdrawal of ${amount:.2f} saved.")

            else:  # Transfer Between Accounts
                txn_out = Transaction(
                    date=transaction_date,
                    account_name=account_name,
                    transaction_type="Transfer Out",
                    amount=-amount,
                    fund_category=fund_category,
                    source_notes=f"Transfer to {transfer_to_account} {source_notes}",
                    transfer_to_account=transfer_to_account,
                )
                txn_in = Transaction(
                    date=transaction_date,
                    account_name=transfer_to_account,
                    transaction_type="Transfer In",
                    amount=amount,
                    fund_category=fund_category,
                    source_notes=f"Transfer from {account_name} {source_notes}",
                )
                insert_transaction_data(txn_out.dict())
                insert_transaction_data(txn_in.dict())
                st.success(f"✅ Transfer of ${amount:.2f} saved.")

        except ValidationError as e:
            for error in e.errors():
                st.error(f"Error in field '{error['loc'][0]}': {error['msg']}")