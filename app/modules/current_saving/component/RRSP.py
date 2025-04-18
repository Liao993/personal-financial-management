import streamlit as st # type: ignore
import pandas as pd
import datetime
from utils.data import years

def RRSP(original_data, room):
  color = '#F38701'  # Orange color for RRSP
  today = datetime.date.today()
  current_year = today.year

  st.markdown(f"<h3 style='text-align: center; color:{color};'>RRSP Contribution Status</h3>", unsafe_allow_html=True)

  selected_year = st.selectbox("Select Year for RRSP Contribution:", years)

  rrsp_data = original_data[original_data['account_name'].str.contains('RRSP', case=False)].copy()
  rrsp_data['date'] = pd.to_datetime(rrsp_data['date'])
  rrsp_amount = rrsp_data['amount'].sum()
  rrsp_contribution = rrsp_data[(rrsp_data['transaction_type'].isin(['Transfer In', 'Deposit']))]['amount'].sum()
  selected_year_contribution = rrsp_data[rrsp_data['transaction_type'].isin(['Transfer In', 'Deposit']) & (rrsp_data['date'].dt.year == selected_year)]['amount'].sum()
  other_year_contribution = rrsp_contribution - selected_year_contribution
  rrsp_withdrawal = rrsp_data[(rrsp_data['transaction_type'].isin(['Transfer Out', 'Withdrawal']))]['amount'].sum() 
  total_room = room
  total_left = total_room - rrsp_contribution

  # Create a dictionary to hold the data
  rrsp_summary_data = {
     'action': [f"{selected_year} Contribution", "Other Year Contribution", 'Total Contribution', 'Total Withdrawal','Total Amount in RRSP',f'Total Room in {current_year}', f'Room Left in {current_year}'],
      'amount': [selected_year_contribution, other_year_contribution, rrsp_contribution, rrsp_withdrawal, rrsp_amount, total_room, total_left]
  }

  # Create a Pandas DataFrame from the dictionary
  rrsp_summary_df = pd.DataFrame(rrsp_summary_data).set_index('action')

  st.dataframe(rrsp_summary_df)