import streamlit as st # type: ignore
import pandas as pd # type: ignore
def saving_sum(transaction):
  # get summary of retire, medium and traveling and group by year and month
    transaction.rename(columns={'fund_category' : "category"}, inplace=True)
    transaction_filtered = transaction[transaction['category'].isin(['Retirement Saving', 'Medium-term Saving', "Traveling Funds"])]
    transaction_filtered = transaction_filtered[transaction_filtered['transaction_type'].isin(['Deposit'])]
    transaction_filtered['month'] = pd.to_datetime(transaction_filtered['date']).dt.month
    transaction_filtered['year'] = pd.to_datetime(transaction_filtered['date']).dt.year

  # to get withdrawl usage for Medium Saving
    transaction_filtered_medium = transaction[transaction['category'].isin(['Medium-term Saving'])]
    transaction_filtered_medium = transaction_filtered_medium[transaction_filtered_medium['transaction_type'].isin(['Withdrawal'])]
    transaction_filtered_medium['month'] = pd.to_datetime(transaction_filtered_medium['date']).dt.month
    transaction_filtered_medium['year'] = pd.to_datetime(transaction_filtered_medium['date']).dt.year

  # 1. Pivot and redesign dataframe format
    st.markdown(f"<h3 style='text-align: center; color: #f1c40f;'>Saving Summary (All Deposit)</h3>", unsafe_allow_html=True)
    summary_pivot = transaction_filtered.pivot_table(
    index=['year', 'month'],
    columns='category',
    values='amount',
    aggfunc='sum'
    ).reset_index()

    # 2. Rename columns to match your desired format (if needed, assuming c1, c2, c3 exist)
    summary_pivot.columns.name = None # Remove the 'category' column name from the index

    # 3. Create the calculated subtotal columns
    
    summary_pivot['Monthly (R+M)'] = summary_pivot['Retirement Saving'] + summary_pivot['Medium-term Saving']
    summary_pivot['Monthly (R+M+T)'] = summary_pivot['Retirement Saving'] + summary_pivot['Medium-term Saving'] + summary_pivot['Traveling Funds']

    # 4. Calculate the total for the month 
  
    summary_pivot['monthly_all_total'] = summary_pivot[['Retirement Saving', 'Medium-term Saving', 'Traveling Funds']].sum(axis=1)
    summary_pivot['monthly_r&m_total'] = summary_pivot[['Retirement Saving', 'Medium-term Saving']].sum(axis=1)

    # 2. Calculate the yearly average from the monthly totals
    yearly_avg = summary_pivot.groupby('year')['monthly_all_total'].mean().reset_index()
    yearly_avg = yearly_avg.rename(columns={'monthly_all_total': 'Monthly Average (R+M+T)'})

    yearly_r_d_avg = summary_pivot.groupby('year')['monthly_r&m_total'].mean().reset_index()
    yearly_r_d_avg = yearly_r_d_avg.rename(columns={'monthly_r&m_total': 'Monthly Average (R+M)'})

    yearly_r_avg = summary_pivot.groupby('year')['Retirement Saving'].mean().reset_index()
    yearly_r_avg = yearly_r_avg.rename(columns={'Retirement Saving': 'Monthly Average (R)'})  

    yearly_m_avg = summary_pivot.groupby('year')['Medium-term Saving'].mean().reset_index()
    yearly_m_avg = yearly_m_avg.rename(columns={'Medium-term Saving': 'Monthly Average (M)'})  
    # 3. Calculate the yearly sum from the monthly totals
    yearly_sum = summary_pivot.groupby('year')['monthly_all_total'].sum().reset_index()
    yearly_sum = yearly_sum.rename(columns={'monthly_all_total': 'Yearly Total (R+M+T)'})
   
    yearly_r_d_sum = summary_pivot.groupby('year')['monthly_r&m_total'].sum().reset_index()
    yearly_r_d_sum = yearly_r_d_sum.rename(columns={'monthly_r&m_total': 'Yearly Total (R+M)'})

    yearly_r_sum = summary_pivot.groupby('year')['Retirement Saving'].sum().reset_index()
    yearly_r_sum = yearly_r_sum.rename(columns={'Retirement Saving': 'Yearly Total (R)'})

    yearly_m_sum = summary_pivot.groupby('year')['Medium-term Saving'].sum().reset_index()
    yearly_m_sum = yearly_m_sum.rename(columns={'Medium-term Saving': 'Yearly Total (M)'})
    
    # 4. Merge show the 4 sum result first and then the average
    final_summary_1 = pd.merge(summary_pivot, yearly_sum, on='year', how='left')
    final_summary_2 = pd.merge(final_summary_1, yearly_r_d_sum, on='year', how='left')
    final_summary_3 = pd.merge(final_summary_2, yearly_r_sum, on='year', how='left')
    final_summary_4 = pd.merge(final_summary_3, yearly_m_sum, on='year', how='left')
    final_summary_5 = pd.merge(final_summary_4, yearly_avg, on='year', how='left')
    final_summary_6 = pd.merge(final_summary_5, yearly_r_d_avg, on='year', how='left')
    final_summary_7 = pd.merge(final_summary_6, yearly_r_avg, on='year', how='left')
    final_summary_8 = pd.merge(final_summary_7, yearly_m_avg, on='year', how='left')
    # 5. add Medium Yearly Withdrawl Amount
    withdrawal_sum = pd.DataFrame(transaction_filtered_medium.groupby('year')['amount'].sum().reset_index().rename(columns={'amount': 'Yearly Medium Withdrawal'}))
    final_summary_9 = pd.merge(final_summary_8, withdrawal_sum, on='year', how='left')

    # 6. Display the result in Streamlit (dropping the temporary monthly_total column if you wish)
    final_summary = final_summary_9.drop(columns=['monthly_all_total', 'monthly_r&m_total']) 
    final_summary = final_summary.sort_values(by=['year', 'month'], ascending=[False, False])
    st.dataframe(final_summary, hide_index=True)
   