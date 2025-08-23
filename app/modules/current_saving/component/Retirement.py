import streamlit as st # type: ignore
import pandas as pd

def Retirement(selected_year, original_data):
  st.markdown(f"<h2 style='text-align: center; color: #3dafdd'>Retirement Saving Status</h2>", unsafe_allow_html=True)

  retirement_data = original_data[original_data['fund_category'] == 'Retirement Saving'].copy()
  retirement_data['date'] = pd.to_datetime(retirement_data['date'])

  retirement_deposit = retirement_data[retirement_data['transaction_type'].isin(['Deposit'])]['amount'].sum()
  selected_year_deposit = retirement_data[retirement_data['transaction_type'].isin(['Deposit']) & (retirement_data['date'].dt.year == selected_year)]['amount'].sum()
  other_year_deposit = retirement_deposit - selected_year_deposit
  retirement_withdrawal = retirement_data[retirement_data['transaction_type'].isin(['Withdrawal'])]['amount'].sum()
  total_amount_left = retirement_deposit + retirement_withdrawal #withdrawal is negative
  
  # Create a dictionary to hold the data
  retirement_summary_data = {
      f"{selected_year} Contribution": [selected_year_deposit],
      "Other Year Contribution": [other_year_deposit],
      'Total Contribution': [retirement_deposit],
      'Total Withdrawal': [retirement_withdrawal],
      'Total Amount Left': [total_amount_left],
  }

  # Create a Pandas DataFrame from the dictionary
  retirement_summary_df = pd.DataFrame(retirement_summary_data)

  st.dataframe(retirement_summary_df, hide_index=True)