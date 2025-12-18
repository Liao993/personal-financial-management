import streamlit as st # type: ignore
import pandas as pd # type: ignore
def saving_sum(transaction):
  # get three summary and group by year and month
    transaction.rename(columns={'fund_category' : "category"}, inplace=True)
    transaction_filtered = transaction[transaction['category'].isin(['Retirement Saving', 'Medium-term Saving', "Traveling Funds"])]
    transaction_filtered = transaction_filtered[transaction_filtered['transaction_type'].isin(['Deposit'])]
    transaction_filtered['month'] = pd.to_datetime(transaction_filtered['date']).dt.month
    transaction_filtered['year'] = pd.to_datetime(transaction_filtered['date']).dt.year

    #redesign dataframe format

    summary_pivot = transaction_filtered.pivot_table(
    index=['year', 'month'],
    columns='category',
    values='amount',
    aggfunc='sum'
    ).reset_index()

    # 2. Rename columns to match your desired format (if needed, assuming c1, c2, c3 exist)
    summary_pivot.columns.name = None # Remove the 'category' column name from the index

    # 3. Create the calculated subtotal columns
    summary_pivot['Retire + Medium'] = summary_pivot['Retirement Saving'] + summary_pivot['Medium-term Saving']
    summary_pivot['All Savings'] = summary_pivot['Retirement Saving'] + summary_pivot['Medium-term Saving'] + summary_pivot['Traveling Funds']

    # 4. Calculate the total for the month 
    summary_pivot['monthly_all_total'] = summary_pivot[['Retirement Saving', 'Medium-term Saving', 'Traveling Funds']].sum(axis=1)
    summary_pivot['monthly_r&m_total'] = summary_pivot[['Retirement Saving', 'Medium-term Saving']].sum(axis=1)

    # 2. Calculate the yearly average from the monthly totals
    yearly_avg = summary_pivot.groupby('year')['monthly_all_total'].mean().reset_index()
    yearly_avg = yearly_avg.rename(columns={'monthly_all_total': 'Yearly Average'})

    yearly_r_d_avg = summary_pivot.groupby('year')['monthly_r&m_total'].mean().reset_index()
    yearly_r_d_avg = yearly_r_d_avg.rename(columns={'monthly_r&m_total': 'Yearly Average (R+M)'})

    # 3. Calculate the yearly sum from the monthly totals
    yearly_sum = summary_pivot.groupby('year')['monthly_all_total'].sum().reset_index()
    yearly_sum = yearly_sum.rename(columns={'monthly_all_total': 'Yearly Total'})
   
    yearly_r_d_sum = summary_pivot.groupby('year')['monthly_r&m_total'].sum().reset_index()
    yearly_r_d_sum = yearly_r_d_sum.rename(columns={'monthly_r&m_total': 'Yearly Total (R+M)'})

    # 4. Merge the yearly average back into the main pivot table
    final_summary_1 = pd.merge(summary_pivot, yearly_r_d_avg, on='year', how='left')
    final_summary_2 = pd.merge(final_summary_1, yearly_avg, on='year', how='left')
    final_summary_3 = pd.merge(final_summary_2, yearly_r_d_sum, on='year', how='left')
    final_summary_4 = pd.merge(final_summary_3, yearly_sum, on='year', how='left')

    # 5. Display the result in Streamlit (dropping the temporary monthly_total column if you wish)
    final_summary = final_summary_4.drop(columns=['monthly_all_total', 'monthly_r&m_total']) 
    final_summary = final_summary.sort_values(by=['year', 'month'], ascending=[False, False])
    st.dataframe(final_summary, hide_index=True)
   