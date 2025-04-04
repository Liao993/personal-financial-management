"""
from app.models.income import Income
from pydantic import ValidationError

def validate_income_data(income_data: dict) -> list:
    errors = []
    try:
        Income(**income_data)  # Try to create the Pydantic model for validation
    except ValidationError as e:
        for error in e.errors():
            field_name = error['loc'][0]
            error_message = error['msg']
            errors.append(f"Error in field '{field_name}': {error_message}")
    return errors

# You can add validation functions for other models here
"""