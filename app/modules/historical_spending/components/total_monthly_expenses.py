import streamlit as st # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import numpy as np # type: ignore
import decimal

def create_monthly_expense_bar_chart(expense):
    st.markdown("<h3 style='text-align: center; color: orange;'>Monthly Expense</h3>", unsafe_allow_html=True)

 
    
    expense['month'] = pd.to_datetime(expense['date']).dt.month
    # divide expense is donation or non donation
    expense['donation'] = expense['category'].apply(lambda x: 'Donation' if x == 'Donation' else 'Non_Donation')

    # 1. Aggregate donation and non-donation amounts separately by month
    summary_data = (
    expense.groupby(['month', 'donation'])['amount']
    .sum()
    .reset_index()
    )
    # 2.Convert Decimal to float
    summary_data['amount'] = summary_data['amount'].apply(decimal.Decimal.__float__)

    # 3.Pivot so each month has two columns: Donation, Non-Donation
    pivot_data = summary_data.pivot(index='month', columns='donation', values='amount').fillna(0)

    # Extract columns
    months = pivot_data.index
    non_donation = pivot_data['Non_Donation']
    donation = pivot_data['Donation']

    # 2. Plot stacked bar chart
    plt.figure(figsize=(10, 8))

    plt.bar(months, non_donation, color='orange', label='Non_Donation')
    plt.bar(months, donation, bottom=non_donation, color='green', label='Donation')

    # Labels
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Amount', fontsize=18)

    # Y-Axis ticks (every 100)
    max_amt = (non_donation + donation).max()
    plt.yticks(np.arange(0, max_amt + 100, 100), fontsize=18)

    # X-Axis
    plt.xticks(
        ticks=range(1, 13),
        labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        fontsize=14
    )

    # Grid
    plt.grid(which='both', axis='y', linestyle='--', color='gray', linewidth=0.5)

    # Legend (horizontal bottom)
    plt.legend(
        fontsize=16,
    
        ncol=2
    )

    plt.tight_layout()
    st.pyplot(plt.gcf(), use_container_width=True)

   

