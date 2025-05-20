
import streamlit as st # type: ignore
from backend.trip_backend import fetch_trip_selection

def selected_the_trip():
  with st.form("trip_selection") as form:
    trip_list = fetch_trip_selection()
    col1, col2 = st.columns(2)
    with col1:
      your_trip = st.selectbox("Please select a trip", trip_list, index=1)
    with col2:
      submit_button = st.form_submit_button("Submit")
      
  if submit_button:
    return your_trip
      