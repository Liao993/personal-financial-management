
import streamlit as st # type: ignore
import pandas as pd
import datetime

from utils.data import years

def TFSA(original_data, room):
    color = '#69B41E'
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    st.markdown(f"<h3 style='text-align: center; color:{color};'>TFSA Contribution Status</h3>", unsafe_allow_html=True)

    
    selected_year = st.selectbox("Select Year for TFSA Contribution:", years)

    tfsa_data = original_data[original_data['account_name'].str.contains('TFSA', case=False)].copy() # Create a copy to avoid modifying the original DataFrame

    # Convert the 'date' column to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(tfsa_data['date']):
        tfsa_data['date'] = pd.to_datetime(tfsa_data['date'])

  
    total_amount = tfsa_data['amount'].sum()
    total_contribution = tfsa_data[(tfsa_data['transaction_type'].isin(['Transfer In', 'Deposit']))]['amount'].sum()

    # TFSA Contribution Room Re-built
    if current_month == 1 and current_day == 1:
        total_contribution = total_amount
    else:
        total_contribution = total_contribution

    selected_year_contribution = tfsa_data[(tfsa_data['date'].dt.year == selected_year)]['amount'].sum()
    other_year_contribution = total_contribution - selected_year_contribution
    total_withdrawal = tfsa_data[(tfsa_data['transaction_type'].isin(['Transfer Out', 'Withdrawal']))]['amount'].sum() 
    total_room = room
    total_left = total_room - total_contribution
    
    # Create a dictionary to hold the data
    tfsa_summary_data = {
        'action': [f"{selected_year} Contribution", "Other Year Contribution", 'Total Contribution', 'Total Withdrawal','Total Amount in TFSA',f'Total Room in {current_year}', f'Room Left in {current_year}'],
        'amount': [selected_year_contribution, other_year_contribution, total_contribution, total_withdrawal, total_amount, total_room, total_left]
    }

    # Create a Pandas DataFrame from the dictionary
    tfsa_summary_df = pd.DataFrame(tfsa_summary_data).set_index('action')
    
    st.dataframe(tfsa_summary_df)
