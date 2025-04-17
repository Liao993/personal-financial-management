from datetime import datetime
import streamlit as st # type: ignore
from backend.transaction_backend import insert_transaction_data  # Assuming you have this function
from models.transaction_models import Transaction  # Import your Pydantic model

def save_monthly_savings(goal_datetime, source_notes, travel_saving, retirement_saving, medium_term_saving, rbc_saving):
    
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

    insert_data = []
    for transaction in transactions_to_insert:
        try:
            validated_data = Transaction(**transaction.dict()) # Validate against the Pydantic model
            insert_data.append(validated_data.dict())
        except Exception as e:
            st.error(f"Validation error for transaction: {transaction.dict()}. Error: {e}")
            return False  # Stop if any validation fails

    if insert_data:
        for data in insert_data:
            insert_transaction_data(data)  # Assuming this function handles single inserts
        st.success("Monthly savings recorded in transactions.")
        return True
    else:
        st.warning("No valid transaction data to insert.")
        return False