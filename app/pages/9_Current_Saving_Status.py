import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data
from utils.data import fund_categories

st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def current_saving_status():
    st.markdown("<h1 style='text-align: center;'>My Saving Status</h1>", unsafe_allow_html=True)

    columns_names , all_data = fetch_all_transaction_data()
    original_data = pd.DataFrame(all_data, columns=columns_names)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h3 style='text-align: center; color:#e56b6f'>Fund Category Current Status</h3>", unsafe_allow_html=True)
        total_fund_status = original_data.groupby('fund_category')['amount'].sum().reindex(fund_categories).fillna(0).reset_index()
        # Set the index to fund category

        st.dataframe(total_fund_status.set_index('fund_category'))
       
    with col2:
        st.markdown("<h3 style='text-align: center; color:#e5de00'>Account Current Status</h3>", unsafe_allow_html=True)
        account_status = original_data.groupby('account_name')['amount'].sum().reset_index()
        st.dataframe(account_status.set_index('account_name'))
    with col3:
        st.markdown("<h3 style='text-align: center; color:#2a9df4'>Chequing Current Status</h3>", unsafe_allow_html=True)
        rbc_status = original_data[original_data['account_name'] == 'RBC Chequing'].groupby('fund_category')['amount'].sum().reset_index()
        st.dataframe(rbc_status.set_index('fund_category'))

  
if __name__ == "__main__":
    current_saving_status()