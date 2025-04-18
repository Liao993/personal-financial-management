import streamlit as st # type: ignore
import pandas as pd

def Medium_Term(selected_year, original_data):


  st.markdown(f"<h5 style='text-align: center; color: #3dafdd'>Medium-Term Saving Status</h5>", unsafe_allow_html=True)

  medium_term_data = original_data[original_data['fund_category'] == 'Medium-term Saving'].copy()
  medium_term_data['date'] = pd.to_datetime(medium_term_data['date'])

  medium_term_deposit = medium_term_data[medium_term_data['transaction_type'].isin(['Deposit'])]['amount'].sum()
  selected_year_deposit = medium_term_data[medium_term_data['transaction_type'].isin(['Deposit']) & (medium_term_data['date'].dt.year == selected_year)]['amount'].sum()
  other_year_deposit = medium_term_deposit - selected_year_deposit
  medium_term_withdrawal = medium_term_data[medium_term_data['transaction_type'].isin(['Withdrawal'])]['amount'].sum()
  medium_term_left = medium_term_deposit + medium_term_withdrawal #withdrawal is negative

  # Create a dictionary to hold the data
  medium_term_summary_data = {
      f"{selected_year} Contribution": [selected_year_deposit],
      "Other Year Contribution": [other_year_deposit],
      'Total Contribution': [medium_term_deposit],
      'Total Withdrawal': [medium_term_withdrawal],
      'Total Amount Left': [medium_term_left],
  }

  # Create a Pandas DataFrame from the dictionary
  medium_term_summary_df = pd.DataFrame(medium_term_summary_data)

  st.dataframe(medium_term_summary_df, hide_index=True)