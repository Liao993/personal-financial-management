import streamlit as st # type: ignore
import pandas as pd

from utils.data import years

def RRSP(original_data, room):
  color = '#F38701'  # Orange color for RRSP

  st.markdown(f"<h3 style='text-align: center; color:{color};'>RRSP Contribution Status</h3>", unsafe_allow_html=True)

  selected_year = st.selectbox("Select Year for RRSP Contribution:", years)

  rrsp_data = original_data[original_data['account_name'].str.contains('RRSP', case=False)].copy()
  rrsp_data['date'] = pd.to_datetime(rrsp_data['date'])

  rrsp_contribution = rrsp_data[(rrsp_data['transaction_type'].isin(['Transfer In', 'Deposit']))]['amount'].sum()
  selected_year_contribution = rrsp_data[rrsp_data['transaction_type'].isin(['Transfer In', 'Deposit']) & (rrsp_data['date'].dt.year == selected_year)]['amount'].sum()
  other_year_contribution = rrsp_contribution - selected_year_contribution
  rrsp_withdrawal = rrsp_data[(rrsp_data['transaction_type'].isin(['Transfer Out', 'Withdrawal']))]['amount'].sum()
  total_room = room
  total_left = total_room - rrsp_contribution

  # Create a dictionary to hold the data
  rrsp_summary_data = {
      'action': [f"{selected_year} Contribution", "Other Year Contribution", 'Total Contribution', 'Total Withdrawal', 'Total Room', 'Room Left'],
      'amount': [selected_year_contribution, other_year_contribution, rrsp_contribution, rrsp_withdrawal, total_room, total_left]
  }

  # Create a Pandas DataFrame from the dictionary
  rrsp_summary_df = pd.DataFrame(rrsp_summary_data).set_index('action')

  st.dataframe(rrsp_summary_df)