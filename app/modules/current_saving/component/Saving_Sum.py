import streamlit as st # type: ignore
import pandas as pd # type: ignore

def saving_sum(transaction):
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

    # --- YEARLY SUMMARY (DEPOSIT, WITHDRAWAL, BALANCE) ---
    txn_yearly = transaction[transaction['category'].isin(['Retirement Saving', 'Medium-term Saving', 'Traveling Funds'])].copy()
    txn_yearly = txn_yearly[txn_yearly['transaction_type'].isin(['Deposit', 'Withdrawal'])]
    txn_yearly['year'] = pd.to_datetime(txn_yearly['date']).dt.year
    txn_yearly['month'] = pd.to_datetime(txn_yearly['date']).dt.month
    
    final_data = []
    if not txn_yearly.empty:
        # Group by unique years, sorting smallest to largest for left-to-right intuitive reading
        for year in sorted(txn_yearly['year'].unique(), reverse=False):
            year_df = txn_yearly[txn_yearly['year'] == year]
            
            def get_sums(categories):
                cat_df = year_df[year_df['category'].isin(categories)]
                deposit = cat_df[cat_df['transaction_type'] == 'Deposit']['amount'].sum()
                withdrawal = cat_df[cat_df['transaction_type'] == 'Withdrawal']['amount'].sum()
                balance = deposit + withdrawal
                return deposit, withdrawal, balance
                
            r_dep, r_wth, r_bal = get_sums(['Retirement Saving'])
            m_dep, m_wth, m_bal = get_sums(['Medium-term Saving'])
            t_dep, t_wth, t_bal = get_sums(['Traveling Funds'])
            rm_dep, rm_wth, rm_bal = get_sums(['Retirement Saving', 'Medium-term Saving'])
            rmt_dep, rmt_wth, rmt_bal = get_sums(['Retirement Saving', 'Medium-term Saving', 'Traveling Funds'])
            
            row = {
                'Year': str(year),
                
                'R - Yearly Deposit': float(r_dep),
                'R - Yearly Withdrawal': float(r_wth),
                'R - Balance': float(r_bal),

                'M - Yearly Deposit': float(m_dep),
                'M - Yearly Withdrawal': float(m_wth),
                'M - Balance': float(m_bal),

                'T - Yearly Deposit': float(t_dep),
                'T - Yearly Withdrawal': float(t_wth),
                'T - Balance': float(t_bal),

                '(R+M) - Yearly Deposit': float(rm_dep),
                '(R+M) - Yearly Withdrawal': float(rm_wth),
                '(R+M) - Balance': float(rm_bal),

                '(R+M+T) - Yearly Deposit': float(rmt_dep),
                '(R+M+T) - Yearly Withdrawal': float(rmt_wth),
                '(R+M+T) - Balance': float(rmt_bal),
            }
            final_data.append(row)
            
    yearly_summary = pd.DataFrame(final_data)
    if not yearly_summary.empty:
        # Transpose dataframe so Years are columns and Metrics are rows
        yearly_summary.set_index('Year', inplace=True)
        yearly_summary = yearly_summary.T.reset_index()
        yearly_summary.rename(columns={'index': 'Metrics'}, inplace=True)

    # --- UI DISPLAY ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='text-align: center; color: #f1c40f;'>Yearly Saving Summary</h3>", unsafe_allow_html=True)
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