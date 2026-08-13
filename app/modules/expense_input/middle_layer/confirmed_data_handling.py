import streamlit as st # type: ignore
from utils.validation import validate_expense_data
from backend.expense_backend import find_manual_duplicate_expense, insert_expense_data


def describe_manual_duplicate(expense_data: dict) -> str:
    return (
        f"{expense_data.get('date')} | {expense_data.get('payment_method')} | "
        f"{expense_data.get('category')} | {expense_data.get('amount')}"
    )


def confirmed_data_handling(reviewed_data, data_saved_key):
    """
    Handles data processing after the user confirms the input.
    """
    expense_data = reviewed_data
    if validate_expense_data(expense_data):
        existing_matches = find_manual_duplicate_expense(expense_data)
        if not existing_matches.empty:
            st.error(
                "This manual expense looks duplicated, so it was not saved. "
                "Manual duplicate checks use Date, Category, Amount, and Payment Method."
            )
            st.warning(describe_manual_duplicate(expense_data))
            st.dataframe(existing_matches, use_container_width=True, hide_index=True)
            return

        st.info("Data is saving to database .......")
        if insert_expense_data(expense_data):
            st.session_state[data_saved_key] = True  # Set data_saved_key to True
            st.rerun()
    else:
        pass
