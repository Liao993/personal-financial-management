import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data
from backend.retirement_limits_backend import (
    fetch_retirement_limits,
    update_retirement_limits,
)
from modules.current_saving.component.TFSA import TFSA
from modules.current_saving.component.RRSP import RRSP


st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def TFSA_and_RRSP():
    st.markdown("<h1 style='text-align: center;'>TFSA and RRSP</h1>", unsafe_allow_html=True)

    limits = fetch_retirement_limits()
    with st.expander("Edit total contribution limits", expanded=False):
        with st.form("retirement_account_limits_form"):
            tfsa_limit = st.number_input(
                "TFSA total limit",
                min_value=0.0,
                value=float(limits["TFSA"]),
                step=100.0,
                format="%.2f",
            )
            rrsp_limit = st.number_input(
                "RRSP total limit",
                min_value=0.0,
                value=float(limits["RRSP"]),
                step=100.0,
                format="%.2f",
            )
            if st.form_submit_button("Save limits"):
                update_retirement_limits(tfsa_limit, rrsp_limit)
                limits["TFSA"] = tfsa_limit
                limits["RRSP"] = rrsp_limit
                st.success("TFSA and RRSP limits updated.")

    columns_names , all_data = fetch_all_transaction_data()
    original_data = pd.DataFrame(all_data, columns=columns_names)

    col1, col2 = st.columns(2)

   
    with col1:
        TFSA(original_data, limits["TFSA"])
    with col2:
        RRSP(original_data, limits["RRSP"])

if __name__ == "__main__":
    TFSA_and_RRSP()
