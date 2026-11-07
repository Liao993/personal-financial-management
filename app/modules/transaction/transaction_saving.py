from datetime import datetime
import streamlit as st  # type: ignore
from backend.transaction_backend import insert_transaction_data
from models.transaction_models import Transaction


def process_transactions_and_save(transactions):
    insert_successful = True
    for transaction_data in transactions:
        try:
            transaction = Transaction(
                date=transaction_data.get("Transaction Date"),
                account_name=transaction_data.get("Account Name"),
                transaction_type=transaction_data.get("Transaction Type"),
                amount=transaction_data.get("Amount"),
                fund_category=transaction_data.get("Usable Fund Category"),
                source_notes=transaction_data.get("Notes"),
                transfer_to_account=transaction_data.get("Transfer To Account"),
            )
            validated_data = transaction.dict()
            success = insert_transaction_data(validated_data)
            if not success:
                insert_successful = False
                st.error(f"Failed to insert transaction: {transaction_data}")
        except Exception as e:
            st.error(
                f"Validation or insertion error for transaction: "
                f"{transaction_data}. Error: {e}"
            )
            return False
    return insert_successful


def transaction_savings_action(returned_transaction_data):
    if returned_transaction_data:
        success = process_transactions_and_save(returned_transaction_data)
        return success
    else:
        st.warning("No transaction data was available to save.")
        return False
