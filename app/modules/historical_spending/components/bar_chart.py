import streamlit as st # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_summary_bar_chart(data):
    st.markdown("<h3 style='text-align: center;'>Expense Distribution by Summary Category</h3>", unsafe_allow_html=True)

    # Group data by 'summary_category' and calculate the sum of 'amount'
    summary_data = data.groupby('summary_category')['amount'].sum().reset_index()

    # Calculate total amount for percentage calculations
    total_amount = summary_data['amount'].sum()
    summary_data['percentage'] = (summary_data['amount'] / total_amount) * 100

    # Create the horizontal bar chart using Seaborn
    plt.figure(figsize=(10, 8))  # Adjust figure size as needed
    ax = sns.barplot(x='amount', y='summary_category', data=summary_data)
    plt.xlabel('Amount')
    plt.ylabel('Category')

    # Add annotations
    for index, row in summary_data.iterrows():
        ax.text(row['amount'], index,  # x, y
                f"${row['amount']:.2f}\n({row['percentage']:.1f}%)",  # text
                color='black', ha='left', va='center')

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    st.pyplot(plt.gcf(), use_container_width=True)

