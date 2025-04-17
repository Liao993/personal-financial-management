from datetime import datetime
import streamlit as st # type: ignore
from backend.transaction_backend import insert_transaction_data  # Assuming you have this function
from models.transaction_models import Transaction  # Import your Pydantic model

# Function to handle the list of transaction data and insert it into the database
def process_transactions_and_save(transactions):
    insert_successful = True
    for transaction_data in transactions:
        try:
            # Map the keys from your dictionary to the Transaction model fields
            transaction = Transaction(
                date=transaction_data.get('Transaction Date'),
                account_name=transaction_data.get('Account Name'),
                transaction_type=transaction_data.get('Transaction Type'),
                amount=transaction_data.get('Amount'),
                fund_category=transaction_data.get('Usable Fund Category'),
                source_notes=transaction_data.get('Notes'),
                transfer_to_account=transaction_data.get('Transfer To Account'),
                transfer_to_fund_category=transaction_data.get('Transfer To Funds'),
            )
            validated_data = transaction.dict() # Get dictionary for database insertion
            success = insert_transaction_data(validated_data)
            if not success:
                insert_successful = False
                st.error(f"Failed to insert transaction: {transaction_data}") # More specific error
        except Exception as e:
            st.error(f"Validation or insertion error for transaction: {transaction_data}. Error: {e}")
            return False  # Stop if any validation or insertion fails
    return insert_successful

# to be called in the Page when Save the Results button clicked
def transaction_savings_action(returned_transaction_data):
    if returned_transaction_data:
        success = process_transactions_and_save(returned_transaction_data)
        if success:
            st.success("Transaction data has been saved successfully!")
        else:
            st.error("Failed to save transaction data. Please check the error messages above.")
    else:
        st.warning("No transaction data was available to save.")
