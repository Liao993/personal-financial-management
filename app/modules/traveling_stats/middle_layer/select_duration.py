
import streamlit as st # type: ignore

def selected_year_choice(key1, key2):
  year_list = [2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035]
  year_from = st.selectbox("Please select the STARTING year", year_list, key=key1)
  year_end = st.selectbox("Please select the END year", year_list, key=key2)
  