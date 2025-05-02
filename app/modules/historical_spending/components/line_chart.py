import streamlit as st  # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_line_chart(data, annual_income):
    # Calculate monthly income
    monthly_income = annual_income / 12
    data['income'] = monthly_income # set monthly income

    st.markdown(f"<h3 style='text-align: center; color: #e67e22;'>Percentage of Monthly Expense by Category </h3>", unsafe_allow_html=True)
    
    # Extract the month from the 'date' column
    data['date'] = pd.to_datetime(data['date'])
    data['month'] = data['date'].dt.month

    # Filter for the specified categories
    categories_of_interest = ['Grocery', 'Food Outside', 'Home Deposit', 'Donation']
    data['major_category'] = data['category'].apply(lambda x: x if x in categories_of_interest else 'Others')

    # Group data
    grouped = (
        data.groupby(['month', 'major_category'], as_index=False)['amount']
        .sum()
        .rename(columns={'amount': 'total_amount'})
    )

    # Create full month-category grid
    all_months = pd.Series(range(1, 13), name='month')
    all_categories = pd.Series(data['major_category'].unique(), name='major_category')
    full_grid = pd.merge(all_months.to_frame(), all_categories.to_frame(), how='cross')

    # Join grouped data with full grid
    monthly_expenses = pd.merge(full_grid, grouped, on=['month', 'major_category'], how='left')
    monthly_expenses['total_amount'] = monthly_expenses['total_amount'].fillna(0)

    # Compute percentage
    monthly_expenses['percentage'] = (monthly_expenses['total_amount'] / int(monthly_income)) * 100

    # Define colors
    category_colors = {
        'Grocery': 'orange',
        'Food Outside': '#5dade2',
        'Home Deposit': '#16a085',
        'Donation': 'red',
        'Others': 'lightgray'
    }
    palette = {cat: category_colors.get(cat, 'gray') for cat in all_categories}

    # Plot
    plt.figure(figsize=(10, 8))
    ax = sns.lineplot(
        data=monthly_expenses,
        x='month',
        y='percentage',
        hue='major_category',
        palette=palette,
        marker='o',
        linewidth=3,
        markersize=8,
        dashes=False
    )

    plt.title(f'Avg. Monthly Income: ${monthly_income:.2f}', loc='right', fontsize=20)
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Percentage of Earning', fontsize=22)
    plt.xticks(
        ticks=range(1, 13),
        labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        fontsize=14
    )
    plt.yticks(fontsize=14)
    plt.grid(axis='y')
    plt.tight_layout()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    st.pyplot(plt.gcf(), use_container_width=True)

