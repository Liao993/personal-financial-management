import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def create_monthly_line_chart(expense, income, transaction):
    st.write("")
    st.markdown(f"<h3 style='text-align: center;'>Percentage of Spending and Saving Balance by Month</h3>", unsafe_allow_html=True)
   # Extract the month from the 'date' column
    expense['date'] = pd.to_datetime(expense['date'])
    expense['month'] = expense['date'].dt.month
  
    # Get Total Spending by Month
    total_monthly_spending = expense.groupby('month', as_index=False)['amount'].sum().rename(columns={'amount': 'total_amount'})
    total_monthly_spending['category'] = "Total Spending"

    # Get Home Spending data
    monthly_home = expense[expense['summary_category'] == "House"].groupby('month', as_index=False)['amount'].sum().rename(columns={'amount': 'total_amount'})
    monthly_home['category'] = 'House'

    # Transaction Category
    transaction.rename(columns={'fund_category' : "category"}, inplace=True)
    transaction_filtered = transaction[transaction['category'].isin(['Retirement Saving', 'Medium-term Saving'])]

    # Concatenate the dataframes
    data = pd.concat([total_monthly_spending, monthly_home, transaction_filtered], ignore_index=True)

    merged_df = pd.merge(data, income, on='month', how='left')
    merged_df['total_income'].fillna(0, inplace=True)

    # Compute percentage with null income treatment
    merged_df['percentage'] = merged_df.apply(
        lambda row: (row['total_amount'] / row['total_income']) * 100 if row['total_income'] != 0 else 0,
        axis=1
    )


    all_categories = merged_df['category'].unique()
    # Define colors
    category_colors = {
        'Total Spending': 'red',
        'House': '#16a085',
        'Retirement Saving': '#1AA7EC',
        'Medium-term Saving': '#f39c12' #orange
    }
    palette = {cat: category_colors.get(cat, 'gray') for cat in all_categories}

    # Plot
    plt.figure(figsize=(20, 8))
    ax = sns.lineplot(
        data=merged_df,
        x='month',
        y='percentage',
        hue='category',
        palette=palette,
        marker='o',
        linewidth=3,
        markersize=8,
        dashes=False
    )
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Percentage of Earning', fontsize=22)
    plt.xticks(
        ticks=range(1, 13),
        labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        fontsize=14
    )
    plt.yticks(ticks=range(0, 110, 10), fontsize=14)
    plt.grid(axis='y')
    plt.tight_layout()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.ylim(0, 100)
    plt.legend(fontsize=20)
    st.pyplot(plt.gcf(), use_container_width=True)

