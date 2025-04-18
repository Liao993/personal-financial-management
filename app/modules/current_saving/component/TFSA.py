
import streamlit as st # type: ignore
import pandas as pd

from utils.data import years

def TFSA(original_data, room):
  color = '#69B41E'

  st.markdown(f"<h3 style='text-align: center; color:{color};'>TFSA Contribution Status</h3>", unsafe_allow_html=True)

  
  selected_year = st.selectbox("Select Year for TFSA Contribution:", years)

  TFSA_data = original_data[original_data['account_name'].str.contains('TFSA', case=False)]
  
 
  TFSA_deposit = TFSA_data[(TFSA_data['transaction_type'] == 'Transfer In') | (TFSA_data['transaction_type'] == 'Deposit')]['amount'].sum()
  selected_year_deposit =  TFSA_data[((TFSA_data['transaction_type'] == 'Transfer In') | (TFSA_data['transaction_type'] == 'Deposit')) & (TFSA_data['date'].dt.year == selected_year)]['amount'].sum()
  other_year_deposit = TFSA_deposit - selected_year_deposit
  TFSA_withdrawal = TFSA_data[(TFSA_data['transaction_type'] == 'Transfer Out') | (TFSA_data['transaction_type'] == 'Withdrawal')]['amount'].sum()
  Total_room = room
  Total_left = Total_room - TFSA_deposit
 
  # Create a dictionary to hold the data
  tfsa_summary_data = {
      'action': [f"{selected_year} Contribution", "Other Year Contribution", 'Total Contribution', 'Total Withdrawal', 'Total Room', 'Room Left'],
      'amount': [selected_year_deposit, other_year_deposit, TFSA_deposit, TFSA_withdrawal, Total_room, Total_left]
  }

  # Create a Pandas DataFrame from the dictionary
  tfsa_summary_df = pd.DataFrame(tfsa_summary_data).set_index('action')
 

  
 
  st.dataframe(tfsa_summary_df)
