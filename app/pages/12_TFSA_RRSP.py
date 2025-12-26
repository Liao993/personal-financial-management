import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data
from modules.current_saving.component.TFSA import TFSA
from modules.current_saving.component.RRSP import RRSP

from utils.data import TFSA_room, RRSP_room


st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def TFSA_and_RRSP():
    st.markdown("<h1 style='text-align: center;'>TFSA and RRSP</h1>", unsafe_allow_html=True)

    columns_names , all_data = fetch_all_transaction_data()
    original_data = pd.DataFrame(all_data, columns=columns_names)

    col1, col2 = st.columns(2)

   
    with col1:
        TFSA(original_data, TFSA_room)
    with col2:
        RRSP(original_data, RRSP_room)

if __name__ == "__main__":
    TFSA_and_RRSP()