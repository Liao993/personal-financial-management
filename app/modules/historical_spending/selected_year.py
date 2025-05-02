import streamlit as st # type: ignore

def selected_year_choice(key):
  year_list = ["All", 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035]
  selected_year = st.selectbox("Please select a year", year_list, key=key)
  return selected_year
  