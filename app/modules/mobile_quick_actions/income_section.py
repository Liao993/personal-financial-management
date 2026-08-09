import streamlit as st  # type: ignore
from datetime import date

from utils.data import fixed_income_data
from utils.validation import validate_income_data
from backend.income_backend import insert_income_data

INCOME_SOURCE_OPTIONS = ["Gov", "Tax Return", "Other"]


def render_income_section():
    st.subheader("💰 Quick Income")
    if st.session_state.pop("mobile_income_success_message", None):
        st.success("Income saved.")

    form_version = st.session_state.get("mobile_income_form_version", 0)
    with st.form(f"mobile_income_form_{form_version}"):
        income_date = st.date_input("Date", value=date.today(), key=f"mobile_income_date_{form_version}")
        income_amount = st.number_input(
            "Amount",
            min_value=0.0,
            format="%.2f",
            value=fixed_income_data,
            key=f"mobile_income_amount_{form_version}",
        )
        income_source = st.selectbox("Source", INCOME_SOURCE_OPTIONS, key=f"mobile_income_source_{form_version}")
        income_regular = st.checkbox("Regular Income", value=True, key=f"mobile_income_regular_{form_version}")
        notes_input = st.text_input("Notes (optional)", "", key=f"mobile_income_notes_{form_version}")
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
            st.session_state["mobile_income_success_message"] = True
            st.session_state["mobile_income_form_version"] = form_version + 1
            st.rerun()
