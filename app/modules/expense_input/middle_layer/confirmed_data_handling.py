import streamlit as st # type: ignore
import time
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data, insert_expense_data_with_source
from datetime import date


def confirmed_data_handling(reviewed_data, data_saved_key):
    """
    Handles data processing after the user confirms the input.
    """
    expense_data = reviewed_data
    if validate_expense_data(expense_data):
        # add source_notes to expense_data
        expense_data['source_notes'] = "Manual Input"
        st.info("Data is saving to database .......")
        time.sleep(3)
        #insert_expense_data(expense_data)
        insert_expense_data_with_source(expense_data)
        st.session_state[data_saved_key] = True  # Set data_saved_key to True
        st.rerun()
    else:
        pass