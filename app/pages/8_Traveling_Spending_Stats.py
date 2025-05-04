import streamlit as st # type: ignore
import pandas as pd
from backend.expense_backend import fetch_trip_expense
from modules.traveling_stats.components.traveling_bar_chart import create_trip_spending_stacked_bar_chart
from modules.traveling_stats.middle_layer.select_duration import selected_year_choice

st.set_page_config(page_title="Traveling Stats", page_icon="💰", layout="wide")
edit_mode = 'regular_edit_mode'
year_start_selected = "year_start"
year_end_selected = 'year_end'

def traveling_stats():
    st.markdown(f"<h2 style='text-align: center; color: #1AA7EC;'>Trip Stats</h2>", unsafe_allow_html=True)
    if edit_mode not in st.session_state:
        st.session_state[edit_mode] = True

    selected_year = None

    if st.session_state[edit_mode]:
        selected_year_choice(year_start_selected, year_end_selected)  # Pass the key
        if st.button("Submit", key="submit_year"):
            st.session_state[edit_mode] = False
            st.rerun()

    else:
        year_start = st.session_state.get(year_start_selected)  # Access using the key
        year_end = st.session_state.get(year_end_selected)  # Access using the key
        if (year_start) is not None and (year_end) is not None:

          all_fetched_expense = fetch_trip_expense(year_start, year_end)

          if (len(all_fetched_expense) == 0):
                st.warning("No Traveling in the selected year")
                if st.button("Choose Again", key="choose_again"):
                    st.session_state[edit_mode] = True
                    st.rerun()
          else:
            col1, col2 = st.columns([0.3, 0.7])  # Create two columns with ratios 0.8 and 0.2
            
            trip_total_df = all_fetched_expense[['trip', 'total_spending']].drop_duplicates()
            total_spending_sum = trip_total_df['total_spending'].sum()

            with col1:
              st.markdown(f"<h3 style='text-align: center; color: #e67e22;'>All Trip Total Spending: {total_spending_sum}</h2>", unsafe_allow_html=True)
              st.dataframe(trip_total_df)
            with col2:

              st.markdown(f"<h3 style='text-align: center; color: #e67e22;'>All Individual Trip Spending by Category</h3>", unsafe_allow_html=True)
              create_trip_spending_stacked_bar_chart(all_fetched_expense)

if __name__ == "__main__":
  traveling_stats()