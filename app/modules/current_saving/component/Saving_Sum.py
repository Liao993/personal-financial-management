import streamlit as st # type: ignore
import pandas as pd # type: ignore
from modules.current_saving.calculations import calculate_yearly_fund_summary

def saving_sum(transaction):
    yearly_summary = calculate_yearly_fund_summary(transaction)
    transaction.rename(columns={'fund_category' : 'category'}, inplace=True)
    
    # Ensure amount is numeric for calculations
    transaction['amount'] = pd.to_numeric(transaction['amount'], errors='coerce').fillna(0)

    # --- MONTHLY SUMMARY (DEPOSITS ONLY) ---
    txn_monthly = transaction[transaction['category'].isin(['Retirement Saving', 'Medium-term Saving', 'Traveling Funds'])].copy()
    txn_monthly = txn_monthly[txn_monthly['transaction_type'].isin(['Deposit'])]
    txn_monthly['month'] = pd.to_datetime(txn_monthly['date']).dt.month
    txn_monthly['year'] = pd.to_datetime(txn_monthly['date']).dt.year
    
    if not txn_monthly.empty:
        summary_pivot = txn_monthly.pivot_table(
            index=['year', 'month'],
            columns='category',
            values='amount',
            aggfunc='sum'
        ).reset_index().fillna(0)
        
        summary_pivot.columns.name = None # Remove the 'category' index name
        
        # Ensure targeted columns exist incase some categories have no deposits
        for col in ['Retirement Saving', 'Medium-term Saving', 'Traveling Funds']:
            if col not in summary_pivot.columns:
                summary_pivot[col] = 0.0

        summary_pivot['Monthly (R+M)'] = summary_pivot['Retirement Saving'] + summary_pivot['Medium-term Saving']
        summary_pivot['Monthly (R+M+T)'] = summary_pivot['Retirement Saving'] + summary_pivot['Medium-term Saving'] + summary_pivot['Traveling Funds']
        
        # Add YTD (Yearly) tracking after sorting chronologically
        summary_pivot = summary_pivot.sort_values(by=['year', 'month'], ascending=[True, True])
        summary_pivot['Yearly Retirement Saving (YTD)'] = summary_pivot.groupby('year')['Retirement Saving'].cumsum()
        summary_pivot['Yearly Medium-term Saving (YTD)'] = summary_pivot.groupby('year')['Medium-term Saving'].cumsum()

        # Sort backwards for display
        monthly_summary = summary_pivot.sort_values(by=['year', 'month'], ascending=[False, False])
    else:
        monthly_summary = pd.DataFrame()

    # --- YEARLY SUMMARY (same net-activity definition as Historical Stats) ---
    # --- UI DISPLAY ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='text-align: center; color: #f1c40f;'>Yearly Saving Summary</h3>", unsafe_allow_html=True)
        st.caption("Net Activity includes deposits, withdrawals, and transfer in/out, excluding expense-linked withdrawals; this matches Historical Stats.")
        if not yearly_summary.empty:
            st.dataframe(yearly_summary, hide_index=True, use_container_width=True)
        else:
            st.info("No yearly data available.")
            
    with col2:
        st.markdown("<h3 style='text-align: center; color: #f1c40f;'>Monthly Saving Summary (All Deposit)</h3>", unsafe_allow_html=True)
        if not monthly_summary.empty:
            st.dataframe(monthly_summary, hide_index=True, use_container_width=True)
        else:
            st.info("No monthly data available.")
