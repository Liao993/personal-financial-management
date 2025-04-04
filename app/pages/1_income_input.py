# app/pages/income_input.py
import streamlit as st # type: ignore
from datetime import date
#from app.models.income import Income # type: ignore
#from app.utils.database import get_db_connection, insert_income # type: ignore

st.set_page_config(page_title="Enter Income", page_icon="💰")

def income_input_page():
   
    st.title("Input Your Income Here!")

    with st.form("income_form"):

        st.markdown("### Date")
        income_date = st.date_input(value=date.today())
        st.markdown("### Amount")
        income_amount = st.number_input(min_value=0.0, format="%.2f", value=1717.85)

        st.markdown("### Source")
        source_options = ["Gov", "Tax Return", "Other"]
        selected_source = st.selectbox("", source_options)
        income_source = selected_source

        if selected_source == "Other":
            income_source = st.text_input("Enter Other Source")
            if not income_source:
                st.warning("Please enter the source not from Gov and Tax Return.")
        else:
            pass
        
        income_regular = st.checkbox("Regular Income", value=True)

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not income_source:
                st.error("Source cannot be empty.")
                return
            else:
                st.text(f"Income Source: {income_source}")
                st.text(f"Income Amount: {income_amount}")
                st.text(f"Income Date: {income_date}")
                st.text(f"Income Regular: {income_regular}")

"""
                if submitted:
            income_data = {
                "date": income_date,
                "amount": income_amount,
                "source": income_source,
                "regular": income_regular,
            }

            validation_errors = validate_income_data(income_data)

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                income_model = Income(**income_data)  # Create Pydantic model
                try:
                    insert_income(income_model)  # Call the backend function
                    st.success("Income data saved successfully!")
                except Exception as e:
                    st.error(f"An error occurred while saving data: {e}")
"""

if __name__ == "__main__":
    income_input_page()

