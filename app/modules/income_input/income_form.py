import streamlit as st # type: ignore
from datetime import date
from utils.data import fixed_income_data

def income_input_form(edit_mode_form_key, review_data_key):

  review_button = False

  with st.form("income_form"):
    income_date = st.date_input("Date", value=date.today())
    income_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=fixed_income_data)

    source_options = ["Gov", "Tax Return", "Other"]
    selected_source = st.selectbox("Source", source_options)
    income_source = selected_source

    notes_input = st.text_input("Notes", "")
    notes = notes_input if notes_input else None  # Set notes to None if empty string

    income_regular = st.checkbox("Regular Income", value=True)

    review_button = st.form_submit_button("Review")

  if review_button:
      st.session_state[review_data_key] = {
          "date": income_date,          # Changed key name
          "amount": income_amount,        # Changed key name
          "source": income_source,        # Changed key name
          "regular": income_regular, 
          "notes": notes                # Changed key name
      }
      st.session_state[edit_mode_form_key] = False
      st.session_state['data_saved_income'] = False # Reset saved state when reviewing again
      st.rerun()

  return review_button