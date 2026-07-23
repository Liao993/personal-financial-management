from datetime import datetime
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import time
from backend.transaction_backend import insert_transaction_data
from models.transaction_models import Transaction
from backend.transaction_backend import fetch_transaction_deposit_check
# Get account names from environment variables so public sample data can use
# neutral labels instead of real institution-specific account names.
import os

def monthly_savings_data_handling(
    goal_datetime,
    source_notes,
    travel_saving,
    retirement_saving,
    medium_term_saving,
    emergency_funds,
    home_deposit,
):
    raw_accounts = os.environ.get("ACCOUNT_NAMES", "")
    Chequing_Account = raw_accounts.split(",")[0].strip() if raw_accounts else "Default Chequing"
    House_Account = raw_accounts.split(",")[1].strip() if len(raw_accounts.split(",")) > 1 else "Default House Account"
    transactions_to_insert = [
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=travel_saving,
            fund_category="Traveling Funds",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=retirement_saving,
            fund_category="Retirement Saving",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=medium_term_saving,
            fund_category="Medium-term Saving",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=emergency_funds,
            fund_category="Emergency Funds",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=House_Account,
            transaction_type="Deposit",
            amount=home_deposit,
            fund_category="House",
            source_notes=source_notes,
        ),
    ]

    data = fetch_transaction_deposit_check(
        goal_datetime.year, goal_datetime.month
    )

    if not data.empty:
        st.warning(
            f"Previous deposits for "
            f"{goal_datetime.year}-{goal_datetime.month:02d} found. "
            "Use Rerun Calculation instead."
        )
        return False

    else:
        insertion_errors = []
        st.info(f"Using account: {Chequing_Account} for monthly savings transactions")

        for transaction in transactions_to_insert:
            try:
                validated_data = Transaction(**transaction.dict())
                success = insert_transaction_data(validated_data.dict())
                if not success:
                    insertion_errors.append(validated_data.dict())
            except Exception as e:
                st.error(
                    f"Validation error for transaction: "
                    f"{transaction.dict()}. Error: {e}"
                )

        if insertion_errors:
            st.error(f"Failed to insert some transactions: {insertion_errors}")
        else:
            return True


def monthly_savings_action():
    goal_datetime     = st.session_state.get("goal_datetime")
    source_notes      = st.session_state.get("source_notes")
    travel_saving     = st.session_state.get("travel_saving")
    retirement_saving = st.session_state.get("retirement_saving")
    medium_term_saving= st.session_state.get("medium_term_saving")
    emergency_funds   = st.session_state.get("emergency_funds")
    home_deposit      = st.session_state.get("home_deposit")
   
    status = monthly_savings_data_handling(
        goal_datetime,
        source_notes,
        travel_saving,
        retirement_saving,
        medium_term_saving,
        emergency_funds,
        home_deposit,
    )

    if status:
        st.success("Data is successfully saved!")
