import streamlit as st # type: ignore
from backend.trip_backend import fetch_trip_selection


TRIP_PLACEHOLDER = "Select a trip"


def build_trip_options(trip_list):
  return [TRIP_PLACEHOLDER] + [
    trip for trip in trip_list if trip and str(trip).strip()
  ]


def get_trip_select_index(options, selected_trip):
  if selected_trip in options:
    return options.index(selected_trip)
  return 0


def selected_the_trip():
  trip_list = fetch_trip_selection()
  trip_options = build_trip_options(trip_list)

  if len(trip_options) == 1:
    st.info("No traveling trips found yet.")
    return None

  with st.form("trip_selection") as form:
    col1, col2 = st.columns(2)
    with col1:
      current_trip = st.session_state.get("selected_traveling_trip")
      your_trip = st.selectbox(
        "Please select a trip",
        trip_options,
        index=get_trip_select_index(trip_options, current_trip),
      )
    with col2:
      submit_button = st.form_submit_button("Submit")
      
  if submit_button and your_trip != TRIP_PLACEHOLDER:
    st.session_state["selected_traveling_trip"] = your_trip
    return your_trip

  return st.session_state.get("selected_traveling_trip")
