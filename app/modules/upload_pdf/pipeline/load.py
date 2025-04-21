import streamlit as st # type: ignore

def load_expense_data(updated_dataframe):
    if updated_dataframe is not None:
        st.info(updated_dataframe)
            # Simulate backend saving
        st.info("Saving data to database...")
        return True
    else:
        st.warning("Your data can't be saved")