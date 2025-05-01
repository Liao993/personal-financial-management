import streamlit as st #type:ignore
from modules.historical_spending.selected_year import selected_year_choice
from modules.historical_spending.components.single_annual_kpi import single_annual_kpi
from modules.historical_spending.components.bar_chart import create_summary_bar_chart
from modules.historical_spending.components.line_chart import create_line_chart
from backend.expense_backend import fetch_annual_expense
from backend.income_backend import fetch_annual_income

st.set_page_config(page_title="Historical Stats", page_icon="💰", layout="wide")

result_mode = 'result_mode'
traveling_mode = 'traveling_mode'

def historical_spending():

  if result_mode not in st.session_state:
      st.session_state[result_mode] = False
  
  if traveling_mode not in st.session_state:
      st.session_state[traveling_mode] = False
  
  iftraveling = st.radio()
  selected_year = None  # Initialize selected_year

  if iftraveling == "Traveling":
    st.info("traveling page")
  else:
    st.session_state[result_mode] = False
  
  

  if st.session_state[result_mode]:
    st.markdown("<h1 style='color: lightgreen; text-align: center;'>Historical Stats</h1>", unsafe_allow_html=True)
    selected_year = selected_year_choice()
    st.session_state[result_mode] = True
  else:
    selected_year = st.session_state.get("year_select") # Access the year from session state
    if selected_year == "All Year":
      st.info("Next Step")
    elif selected_year != None:
      all_fetched_expense = fetch_annual_expense(selected_year)
      annual_income = fetch_annual_income(selected_year)

      if (len(all_fetched_expense) == 0) | (annual_income == 0):
        st.warning("No Spending or Annual Income in the selected year")
        if st.button("Choose Again"):
          st.session_state[result_mode] = False
          st.rerun()
      else:
        single_annual_kpi(all_fetched_expense, selected_year, annual_income)
        col1, col2 = st.columns(2)
        with col1:
          create_summary_bar_chart(all_fetched_expense)
        with col2:
          create_line_chart()

if __name__ == "__main__":
  historical_spending()