import streamlit as st # type: ignore
import pandas as pd

from modules.traveling_stats.components.total_traveling_pie_chart import create_annotation_pie_chart
from modules.traveling_stats.components.total_traveling_bar_chart import create_category_spending_bar_chart
from modules.traveling_stats.components.I_spend_traveling_bar_chart import  create_I_spend_bar_chart
from modules.traveling_stats.components.I_spend_traveling_pie_chart import create_I_spend_pie_chart
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
          total_spending = all_fetched_expense['total_spending'].iloc[0] #get the total spending from the first row.
          st.markdown(f"<h3 style='text-align: left; color: #f1c40f;'>Traveling Breakdown - Total Amount: ${total_spending:.2f}</h3>", unsafe_allow_html=True)
          col1, col2 = st.columns(2)
          with col1:
            create_category_spending_bar_chart(all_fetched_expense)
          with col2:
            create_annotation_pie_chart(all_fetched_expense)
          st.divider()
          total_amount_I_spend = all_fetched_expense['total_i_spent'].iloc[0]
          st.markdown(f"<h3 style='text-align: left; color: #3498db'';'>Traveling Breakdown - Total Amount I Spent (Taken From Traveling Funds): ${total_amount_I_spend:.2f}</h3>", unsafe_allow_html=True)
          if total_amount_I_spend <= 0:
            st.warning("No I Spent in the selected trip")
          else:
            col3, col4 = st.columns(2)
            with col3:
              create_I_spend_bar_chart(all_fetched_expense)
            with col4:
              create_I_spend_pie_chart(all_fetched_expense)
          st.divider()
          amount_spend_by_other = total_spending - total_amount_I_spend
          st.markdown(f"<h3 style='text-align: left;'>Traveling Breakdown - Total Amount Spent by Other: ${amount_spend_by_other:.2f}</h3>", unsafe_allow_html=True)

if __name__ == "__main__":
  traveling_stats()