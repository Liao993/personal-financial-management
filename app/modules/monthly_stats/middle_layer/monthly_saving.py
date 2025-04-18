from datetime import datetime
import streamlit as st # type: ignore
from backend.transaction_backend import insert_transaction_data  # Assuming you have this function
from models.transaction_models import Transaction  # Import your Pydantic model

# Function to handle the data and insert it into the database
def monthly_savings_data_handling(goal_datetime, source_notes, travel_saving, retirement_saving, medium_term_saving, rbc_saving):
    transactions_to_insert = [
        Transaction(
            date=goal_datetime,
            account_name="RBC Chequing",
            transaction_type="Deposit",
            amount=travel_saving,
            fund_category="Traveling Funds",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name="RBC Chequing",
            transaction_type="Deposit",
            amount=retirement_saving,
            fund_category="Retirement Saving",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name="RBC Chequing",
            transaction_type="Deposit",
            amount=medium_term_saving,
            fund_category="Medium-term Saving",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name="RBC TFSA",
            transaction_type="Deposit",
            amount=rbc_saving,
            fund_category="Direct Investing",
            source_notes=source_notes,
        ),
    ]

    insert_successful = True
    
    for transaction in transactions_to_insert:
        try:
            validated_data = Transaction(**transaction.dict()) # Validate against the Pydantic model
            success = insert_transaction_data(validated_data.dict())
            if not success:
                insert_successful = False
                st.error(f"Failed to insert transaction: {validated_data.dict()}") # More specific error
        except Exception as e:
            st.error(f"Validation error for transaction: {transaction.dict()}. Error: {e}")
            return False  # Stop if any validation fails
        
    return insert_successful

# to be called in the Page when Save the Results button clicked
def monthly_savings_action():
    goal_datetime = st.session_state.get('goal_datetime')
    source_notes = st.session_state.get('source_notes')
    travel_saving = st.session_state.get('travel_saving')
    retirement_saving = st.session_state.get('retirement_saving')
    medium_term_saving = st.session_state.get('medium_term_saving')
    rbc_saving = st.session_state.get('rbc_saving')

    
    success = monthly_savings_data_handling(goal_datetime, source_notes, travel_saving, retirement_saving, medium_term_saving, rbc_saving)
    if success:
        st.success("Monthly savings have been saved successfully!")
    else:
        st.error("Failed to save monthly savings. Please check your data.")