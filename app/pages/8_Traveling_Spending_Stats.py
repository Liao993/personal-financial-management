import streamlit as st # type: ignore
import pandas as pd

from modules.traveling_stats.components.traveling_pie_chart import create_annotated_pie_chart
from modules.traveling_stats.components.traveling_bar_chart import create_category_spending_bar_chart
from modules.traveling_stats.middle_layer.select_trip import selected_the_trip
from backend.trip_backend import fetch_trip_expense
st.set_page_config(page_title="Traveling Stats", page_icon="💰", layout="wide")


def traveling_stats():
    
    st.markdown(f"<h1 style='text-align: center; color: #1e8449 ;'>Traveling Stats</h1>", unsafe_allow_html=True)
    the_trip = selected_the_trip()
    st.write(" ")
    st.write(" ")
    if the_trip is not None:
        all_fetched_expense = fetch_trip_expense(the_trip)
        if (len(all_fetched_expense) == 0):
          st.warning("No Spending  in the selected trip")
          if st.button("Choose Again", key="choose_again"):
            selected_the_trip()
        else:
          col1, col2 = st.columns(2)
          with col1:
            create_category_spending_bar_chart(all_fetched_expense)
          with col2:
            create_annotated_pie_chart(all_fetched_expense)
    

if __name__ == "__main__":
  traveling_stats()