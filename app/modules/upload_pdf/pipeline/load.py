import streamlit as st # type: ignore
import pandas as pd
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data

def load_expense_data(updated_dataframe):
    if updated_dataframe is not None:
    
        # 2. Convert the 'date' column to datetime.date objects to make sure it is 100% match
        updated_dataframe['date'] = pd.to_datetime(updated_dataframe['date']).dt.date

       # 3. Validate each row and collect valid data
        valid_expenses = []
        for index, row in updated_dataframe.iterrows():
            expense_data = row.to_dict()
            if validate_expense_data(expense_data):
                valid_expenses.append(expense_data)

        if valid_expenses:
            st.success(f"Successfully validated {len(valid_expenses)} expenses.")
            all_insertions_successful = True #track the insertions
            # 4. Insert the valid expenses into the database
            for expense in valid_expenses:
                if not insert_expense_data(expense): #check if the insertion was successful
                    all_insertions_successful = False
            return all_insertions_successful
        else:
            st.error("No valid expenses found in the DataFrame.")
            return False
    else:
        st.error("Input DataFrame is None.")
        return False