import streamlit as st # type: ignore
from models.income import Income
from pydantic import ValidationError # type: ignore

def validate_income_data(income_data: dict) -> bool:
    try:
        Income(**income_data)  # Try to create the Pydantic model for validation
        return True  # Data is valid
    except ValidationError as e:
        st.error("Validation Errors:")
        for error in e.errors():
            field_name = error['loc'][0]
            error_message = error['msg']
            st.error(f"Error in field '{field_name}': {error_message}")
        return False # Data is invalid


