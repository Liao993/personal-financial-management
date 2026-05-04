from datetime import datetime
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import time
from backend.transaction_backend import insert_transaction_data  # Assuming you have this function
from models.transaction_models import Transaction  # Import your Pydantic model
from backend.transaction_backend import fetch_transaction_deposit_check

# Function to handle the data and insert it into the database
def monthly_savings_data_handling(goal_datetime, source_notes, travel_saving, retirement_saving, medium_term_saving, energency_funds, home_deposit):
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
            account_name="RBC Chequing",
            transaction_type="Deposit",
            amount=energency_funds,
            fund_category="Emergency Funds",
            source_notes=source_notes,
        ),
         Transaction(
            date=goal_datetime,
            account_name="TD House",
            transaction_type="Deposit",
            amount=home_deposit,
            fund_category="House",
            source_notes=source_notes,
        )
    ]
    
  
    data = fetch_transaction_deposit_check(goal_datetime.year, goal_datetime.month)

    if not data.empty:
        st.warning(f"Previous deposits for {goal_datetime.year}-0{goal_datetime.month} found")
        return False

    else:
        insertion_errors = []
        for transaction in transactions_to_insert:
            try:
                validated_data = Transaction(**transaction.dict()) # Validate against the Pydantic model
                success = insert_transaction_data(validated_data.dict())
                if not success:
                    insertion_errors.append(validated_data.dict())
            except Exception as e:
                st.error(f"Validation error for transaction: {transaction.dict()}. Error: {e}")

        if insertion_errors:
            st.error(f"Failed to insert some transactions: {insertion_errors}")
            
        else:
            return True

# to be called in the Page when Save the Results button clicked
def monthly_savings_action():
    goal_datetime = st.session_state.get('goal_datetime')
    source_notes = st.session_state.get('source_notes')
    travel_saving = st.session_state.get('travel_saving')
    retirement_saving = st.session_state.get('retirement_saving')
    medium_term_saving = st.session_state.get('medium_term_saving')
    emergency_funds = st.session_state.get('emergency_funds')
    home_deposit = st.session_state.get('home_deposit')

    
    status = monthly_savings_data_handling(goal_datetime, source_notes, travel_saving, retirement_saving, medium_term_saving, emergency_funds, home_deposit)
     
    if status:
        st.success("Data is successfully saved !")
        