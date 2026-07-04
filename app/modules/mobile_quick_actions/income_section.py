import streamlit as st  # type: ignore
from datetime import date

from utils.data import fixed_income_data
from utils.validation import validate_income_data
from backend.income_backend import insert_income_data

INCOME_SOURCE_OPTIONS = ["Gov", "Tax Return", "Other"]


def render_income_section():
    st.subheader("💰 Quick Income")
    with st.form("mobile_income_form"):
        income_date = st.date_input("Date", value=date.today())
        income_amount = st.number_input(
            "Amount", min_value=0.0, format="%.2f", value=fixed_income_data
        )
        income_source = st.selectbox("Source", INCOME_SOURCE_OPTIONS)
        income_regular = st.checkbox("Regular Income", value=True)
        notes_input = st.text_input("Notes (optional)", "")
        submitted = st.form_submit_button("Save Income")

    if submitted:
        income_data = {
            "date": income_date,
            "amount": income_amount,
            "source": income_source,
            "regular": income_regular,
            "notes": notes_input if notes_input else None,
        }
        if validate_income_data(income_data):
            insert_income_data(income_data)
            st.success(f"✅ Income of ${income_amount:.2f} saved.")