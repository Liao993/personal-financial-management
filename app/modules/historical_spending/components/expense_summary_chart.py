import streamlit as st # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

def create_summary_bar_chart(expense):
    st.markdown("<h3 style='text-align: center; color: #5dade2;'>Annual Expense Distribution by Category</h3>", unsafe_allow_html=True)

    # Group data by 'summary_category' and calculate the sum of 'amount'
    summary_data = expense.groupby('category')['amount'].sum().reset_index()
  
    selected_categories = ['Car', 'Cell Phone' , 'Donation', 'Education', 'Food Outside' , 'Gas', 'Gifts', 'Grocery', 'Household Goods' , 'Saved For Love','Transportation']
    #not in slected category is others
    summary_data.loc[~summary_data['category'].isin(selected_categories), 'category'] = 'Others'
    summary_data = summary_data.groupby('category')['amount'].sum().reset_index()
    #order from most to the lease
    summary_data = summary_data.sort_values(by='amount', ascending=False)
   
    
    # Calculate total amount for percentage calculations
    total_amount = summary_data['amount'].sum()
    summary_data['percentage'] = (summary_data['amount'] / total_amount) * 100

    # Create the horizontal bar chart using Seaborn
    plt.figure(figsize=(10, 8))  # Adjust figure size as needed

    ax = sns.barplot(x='amount', y='category', data=summary_data)
  
    plt.ylabel('Category', fontsize=18)
    plt.yticks(fontsize=18)
    plt.xticks(None)
    plt.xlabel(None)

    # Add annotations pct and amount
    for i, row in summary_data.iterrows():
       
        plt.text(row['amount'], row['category'], f"${row['amount']:.2f} ({row['percentage']:.2f}%)", ha='left', va='center', fontsize=16)
        
        
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    st.pyplot(plt.gcf(), use_container_width=True)

