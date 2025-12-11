import streamlit as st # type: ignore
import pandas as pd
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data, insert_expense_data_with_source
from decimal import Decimal

# after verifying the data, load data into the database
def load_expense_data(updated_dataframe, bank):
    if updated_dataframe is not None:
       # 3. Validate each row and collect valid data
        valid_expenses = []
        for index, row in updated_dataframe.iterrows():
            expense_data = row.to_dict()
            expense_data['source_notes'] = bank
            validated = validate_expense_data(expense_data)   

            if validated:
                valid_expenses.append(expense_data)
            else:
                st.error("No valid expenses found in the DataFrame.")
                return False
        for expense in valid_expenses:
            insert_expense_data_with_source(expense) #check if the insertion was successful
        st.success(f"Successfully validated and inserted {len(valid_expenses)} expenses.")
        return True
    else:
        st.error("Input DataFrame is None.")
        return False