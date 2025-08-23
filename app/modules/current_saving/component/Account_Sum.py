import streamlit as st
import pandas as pd

def Account_Sum(original_data):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        chequing = original_data[original_data['account_name'].str.contains('Chequing', case=False)].copy()
        total_chequing = chequing['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: #f1c40f; text-align: center;'><b>Chequing</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_chequing:.2f}</b></p>",
            unsafe_allow_html=True,
        )
       
    with col2:
        chequing = original_data[original_data['account_name'].str.contains('Notice', case=False)].copy()
        total_chequing = chequing['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: #f1c40f; text-align: center;'><b>Notice Savings</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_chequing:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col3:
        chequing = original_data[original_data['account_name'].str.contains('TFSA', case=False)].copy()
        total_chequing = chequing['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: #00ab41; text-align: center;'><b>TFSA</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_chequing:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col4:
        chequing = original_data[original_data['account_name'].str.contains('RRSP', case=False)].copy()
        total_chequing = chequing['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: #00ab41; text-align: center;'><b>RRSP</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_chequing:.2f}</b></p>",
            unsafe_allow_html=True,
        )

    
