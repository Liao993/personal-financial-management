import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fecth_transaction_data # type: ignore

st.set_page_config(page_title="Transaction", page_icon="💰", layout="wide")


def current_saving_status():
    st.markdown("<h1 style='text-align: center;'>Current Saving Status</h1>", unsafe_allow_html=True)

    original_data = pd.DataFrame(fecth_transaction_data())

    if original_data.empty:
        st.warning("No transaction data available.")
        return
    else:
        st.success("Transaction data fetched successfully.")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h3 style='text-align: center;'>Total Fund Category Saving Status</h3>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center;'>Account Saving Status</h3>", unsafe_allow_html=True)
    with col3:
        st.markdown("<h3 style='text-align: center;'>RBC Chequing Fund Category Status</h3>", unsafe_allow_html=True)