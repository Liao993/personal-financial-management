import streamlit as st # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import numpy as np # type: ignore
import decimal

def create_monthly_expense_bar_chart(expense):
    st.markdown("<h3 style='text-align: center; color: orange;'>Monthly Expense</h3>", unsafe_allow_html=True)

 
    
    expense['month'] = pd.to_datetime(expense['date']).dt.month
    summary_data = expense.groupby('month')['amount'].sum().reset_index()
    summary_data['amount'] = summary_data['amount'].apply(decimal.Decimal.__float__)
    # Create the horizontal bar chart using Seaborn
    plt.figure(figsize=(10, 8))  # Adjust figure size as needed
    plt.title("Total Monthly Expense", loc='right', fontsize=20)
    ax = sns.barplot(x='month', y='amount', data=summary_data, color='orange')
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Amount', fontsize=18)
    #200 gap for y axis
    plt.yticks(np.arange(0.00, summary_data['amount'].max() + 100, 100))
    plt.yticks(fontsize=18)
    plt.xticks(fontsize=16)
    plt.grid(which='both', axis='y', linestyle='--', color='gray', linewidth=0.5)


   
        
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    st.pyplot(plt.gcf(), use_container_width=True)

   

