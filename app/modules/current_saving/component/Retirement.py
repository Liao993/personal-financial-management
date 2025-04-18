import streamlit as st # type: ignore
import pandas as pd

def Retirement(selected_year, original_data):
  st.markdown(f"<h5 style='text-align: center; color: #26dec5'>Retirement Saving Status</h5>", unsafe_allow_html=True)

  retirement_data = original_data[original_data['fund_category'] == 'Retirement Saving'].copy()
  retirement_data['date'] = pd.to_datetime(retirement_data['date'])

  retirement_deposit = retirement_data[retirement_data['transaction_type'].isin(['Deposit'])]['amount'].sum()
  selected_year_deposit = retirement_data[retirement_data['transaction_type'].isin(['Deposit']) & (retirement_data['date'].dt.year == selected_year)]['amount'].sum()
  other_year_deposit = retirement_deposit - selected_year_deposit
  retirement_withdrawal = retirement_data[retirement_data['transaction_type'].isin(['Withdrawal'])]['amount'].sum()
  
  # Create a dictionary to hold the data
  retirement_summary_data = {
      f"{selected_year} Contribution": [selected_year_deposit],
      "Other Year Contribution": [other_year_deposit],
      'Total Contribution': [retirement_deposit],
      'Total Withdrawal': [retirement_withdrawal],
  }

  # Create a Pandas DataFrame from the dictionary
  retirement_summary_df = pd.DataFrame(retirement_summary_data)

  st.dataframe(retirement_summary_df, hide_index=True)