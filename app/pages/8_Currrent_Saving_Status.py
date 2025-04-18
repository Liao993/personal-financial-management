import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data
from modules.current_saving.component.TFSA import TFSA
from modules.current_saving.component.RRSP import RRSP
from modules.current_saving.component.Retirement import Retirement
from modules.current_saving.component.Medium import Medium_Term
from utils.data import TFSA_room, RRSP_room, years


st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def current_saving_status():
    st.markdown("<h1 style='text-align: center;'>My Saving Status</h1>", unsafe_allow_html=True)

    columns_names , all_data = fetch_all_transaction_data()
    original_data = pd.DataFrame(all_data, columns=columns_names)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h3 style='text-align: center; color:#e56b6f'>Total Fund Category Current Status</h3>", unsafe_allow_html=True)
        total_fund_status = original_data.groupby('fund_category')['amount'].sum().reset_index()
        st.dataframe(total_fund_status.set_index('fund_category'))
       
    with col2:
        st.markdown("<h3 style='text-align: center; color:#e5de00'>Account Current Status</h3>", unsafe_allow_html=True)
        account_status = original_data.groupby('account_name')['amount'].sum().reset_index()
        st.dataframe(account_status.set_index('account_name'))
    with col3:
        st.markdown("<h3 style='text-align: center; color:#2a9df4'>RBC Chequing Fund Current Status</h3>", unsafe_allow_html=True)
        rbc_status = original_data[original_data['account_name'] == 'RBC Chequing'].groupby('fund_category')['amount'].sum().reset_index()
        st.dataframe(rbc_status.set_index('fund_category'))

    col4, col5, col6 = st.columns(3)

    with col4:
        color = '#3dcedd'
        major_saving = total_fund_status[total_fund_status['fund_category'].isin(['Medium-term Saving', 'Retirement Saving'])]['amount'].sum()
        st.markdown(f"<h3 style='text-align: center; color:{color};'>Retirement & Medium Saving Status</h3>", unsafe_allow_html=True)
        col4_1, col4_2 = st.columns(2)
        with col4_1:
            st.markdown(f"<h5 style='text-align: center; color: #dd423d;'>Current Accumulation:  ${major_saving}</h5>", unsafe_allow_html=True)
        with col4_2:
            selected_year = st.selectbox("Select Year", years)

        Retirement(selected_year, original_data)
        Medium_Term(selected_year, original_data)
    with col5:
        TFSA(original_data, TFSA_room)
    with col6:
        RRSP(original_data, RRSP_room)

if __name__ == "__main__":
    current_saving_status()