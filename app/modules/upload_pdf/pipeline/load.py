import streamlit as st

def load_expense_data(edited_df):
    
    if st.button("Save Edited Data"):
        # In a real application, you would save 'edited_df' to your database or file
        st.success("Edited data saved (this is a placeholder).")
        st.table(edited_df)