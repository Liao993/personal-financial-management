import streamlit as st # type: ignore
import pandas as pd
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data
from decimal import Decimal
def load_expense_data(updated_dataframe):
    if updated_dataframe is not None:
    
        # 2. Convert the 'date' and amount data type
        updated_dataframe['date'] = pd.to_datetime(updated_dataframe['date']).dt.date
        updated_dataframe['amount'] = updated_dataframe['amount'].astype(float)
      

       # 3. Validate each row and collect valid data
        valid_expenses = []
        for index, row in updated_dataframe.iterrows():
            expense_data = row.to_dict()
            if validate_expense_data(expense_data):
                valid_expenses.append(expense_data)

        if valid_expenses:
            st.success(f"Successfully validated {len(valid_expenses)} expenses.")
            # 4. Insert the valid expenses into the database
            for expense in valid_expenses:
                st.info(type(expense['amount']))
                if not insert_expense_data(expense): #check if the insertion was successful
                    st.error(f"Failed to insert expense: {expense}") #print out the error.
                    return False #stop if one fails
            return True
        else:
            st.error("No valid expenses found in the DataFrame.")
            return False
    else:
        st.error("Input DataFrame is None.")
        return False