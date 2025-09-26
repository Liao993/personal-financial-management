import streamlit as st # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_summary_bar_chart(expense, transaction):
    st.markdown("<h3 style='text-align: center; color: #5dade2;'>Expense Distribution by Summary Category</h3>", unsafe_allow_html=True)

    # Group data by 'summary_category' and calculate the sum of 'amount'
    summary_data = expense.groupby('summary_category')['amount'].sum().reset_index()
    # Add House Expense from transaction data
    house_sum = transaction[transaction['fund_category'] == 'House']['total_amount'].sum()
    house_data = {'summary_category': 'House', 'amount': house_sum}
    summary_data = pd.concat([summary_data, pd.DataFrame(house_data, index=[0])], ignore_index=True)
    
    # Calculate total amount for percentage calculations
    total_amount = summary_data['amount'].sum()
    summary_data['percentage'] = (summary_data['amount'] / total_amount) * 100

    # Create the horizontal bar chart using Seaborn
    plt.figure(figsize=(10, 8))  # Adjust figure size as needed
    plt.title("Spending Percentage is calculated by Total Expense", loc='right', fontsize=20)
    ax = sns.barplot(x='amount', y='summary_category', data=summary_data)
    plt.xlabel('Amount', fontsize=18)
    plt.ylabel(None)
    plt.yticks(fontsize=18)
    plt.xticks(fontsize=16)
    # Add annotations
    for index, row in summary_data.iterrows():
        ax.text(row['amount'], index,  # x, y
                f" ${row['amount']:.2f}\n ({row['percentage']:.1f}%)",  # text
                color='black', ha='left', va='center', fontsize=16)
        
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    st.pyplot(plt.gcf(), use_container_width=True)

