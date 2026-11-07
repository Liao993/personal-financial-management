import streamlit as st # type: ignore
import pandas as pd # type: ignore
import os
from modules.current_saving.calculations import (
    calculate_account_flow_summary,
    calculate_fund_category_summary,
)

def saving_sum(transaction):
    category_summary = calculate_fund_category_summary(transaction)
    hidden_accounts = {"Main Chequing"} if os.environ.get("APP_ENV") == "production" else set()
    account_summary = calculate_account_flow_summary(transaction, hidden_accounts=hidden_accounts)

    st.markdown("<h3 style='text-align: center; color: #f1c40f;'>Fund Category Saving Summary</h3>", unsafe_allow_html=True)
    st.caption("Transfer columns are hidden, but transfer in/out are included in Net Saving with direction applied internally. Annual columns provide yearly context for each monthly fund row.")
    if not category_summary.empty:
        st.dataframe(
            category_summary,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Deposit": st.column_config.NumberColumn("Deposit", format="$%.2f"),
                "Withdrawal": st.column_config.NumberColumn("Withdrawal", format="$%.2f"),
                "Net Saving": st.column_config.NumberColumn("Net Saving", format="$%.2f"),
                "Annual Net Saving": st.column_config.NumberColumn("Annual Net Saving", format="$%.2f"),
                "Annual Net Saving (Retire+Medium)": st.column_config.NumberColumn("Annual Net Saving (Retire+Medium)", format="$%.2f"),
                "Annual Net Saving (R+M+T)": st.column_config.NumberColumn("Annual Net Saving (R+M+T)", format="$%.2f"),
                "Annual Net Saving (All)": st.column_config.NumberColumn("Annual Net Saving (All)", format="$%.2f"),
            },
        )
    else:
        st.info("No fund-category saving data available.")

    st.markdown("<h3 style='text-align: center; color: #f1c40f;'>Account Monthly Flow</h3>", unsafe_allow_html=True)
    st.caption("Account view includes transfers so money movement between physical accounts is visible.")
    if not account_summary.empty:
        st.dataframe(
            account_summary,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Deposit": st.column_config.NumberColumn("Deposit", format="$%.2f"),
                "Withdrawal": st.column_config.NumberColumn("Withdrawal", format="$%.2f"),
                "Transfer In": st.column_config.NumberColumn("Transfer In", format="$%.2f"),
                "Transfer Out": st.column_config.NumberColumn("Transfer Out", format="$%.2f"),
                "Net Account Flow": st.column_config.NumberColumn("Net Account Flow", format="$%.2f"),
                "Yearly Net Account Flow": st.column_config.NumberColumn("Yearly Net Account Flow", format="$%.2f"),
            },
        )
    else:
        st.info("No account flow data available.")
