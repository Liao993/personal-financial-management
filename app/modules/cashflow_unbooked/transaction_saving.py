from datetime import datetime
import streamlit as st # type: ignore
from backend.cashflow_backend import insert_cashflow_data  # Assuming you have this function
from models.cashflow_models import Cashflow  # Import your Pydantic model

# Function to handle the list of transaction data and insert it into the database
def process_transactions_and_save(transactions):
    insert_successful = True
    for transaction_data in transactions:
        try:
            # Map the keys from your dictionary to the Transaction model fields
            transaction = Cashflow(
                date=transaction_data.get('Transaction Date'),
                account_name=transaction_data.get('Account Name'),
                transaction_type=transaction_data.get('Transaction Type'),
                amount=transaction_data.get('Amount'),
                payment_purpose=transaction_data.get('Payment Purpose'),
                source_notes=transaction_data.get('Notes'),
                transfer_to_account=transaction_data.get('Transfer To Account'),
            )
            validated_data = transaction.dict() # Get dictionary for database insertion
            success = insert_cashflow_data(validated_data)
            if not success:
                insert_successful = False
                st.error(f"Failed to insert cashflow transaction: {transaction_data}") # More specific error
        except Exception as e:
            st.error(f"Validation or insertion error for cashflow transaction: {transaction_data}. Error: {e}")
            return False  # Stop if any validation or insertion fails
    return insert_successful

# to be called in the Page when Save the Results button clicked
def transaction_savings_action(returned_transaction_data):
    if returned_transaction_data:
        success = process_transactions_and_save(returned_transaction_data)
        return success
    else:
        st.warning("No transaction data was available to save.")
