import streamlit as st  # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

def create_expense_line_chart(expense, income):
    
   

    st.markdown(f"<h3 style='text-align: center; color: #16a085;'>Percentage of Expense of Income by Month by Category </h3>", unsafe_allow_html=True)
    
    # Extract the month from the 'date' column
    expense['date'] = pd.to_datetime(expense['date'])
    expense['month'] = expense['date'].dt.month

    # Filter for the specified categories
    categories_of_interest = ['Grocery', 'Food Outside', 'Donation', 'Gas', "Gifts"]
    expense['major_category'] = expense['category'].apply(lambda x: x if x in categories_of_interest else 'Others')

    # Group data
    grouped = (
        expense.groupby(['month', 'major_category'], as_index=False)['amount']
        .sum()
        .rename(columns={'amount': 'total_amount'})
    )
    
    # Create full month-category grid
    all_months = pd.Series(range(1, 13), name='month')
    all_categories = pd.Series(grouped['major_category'].unique(), name='major_category')
    full_grid = pd.merge(all_months.to_frame(), all_categories.to_frame(), how='cross')

    # Join grouped data with full grid
    monthly_expenses = pd.merge(full_grid, grouped, on=['month', 'major_category'], how='left')
    monthly_expenses['total_amount'] = monthly_expenses['total_amount'].fillna(0)
  

    #Merge Income Data
    merged_df = pd.merge(monthly_expenses, income, on='month', how='left')
    merged_df['total_income'].fillna(0, inplace=True)

    # Compute percentage with null income treatment
    merged_df['percentage'] = merged_df.apply(
        lambda row: (row['total_amount'] / row['total_income']) * 100 if row['total_income'] != 0 else 0,
        axis=1
    )
  
    #Monthly Income

    monthly_income = merged_df[merged_df['total_income'] !=0]['total_income'].mean()
    # Define colors
    category_colors = {
        'Grocery': '#FFA500',
        'Food Outside': '#5dade2',
        'Gas': "#CA39C8",
        'Donation': "#e62922",
        'Others': "#592F83",
        'Gifts': "#3A6A3A"
    }
    palette = {cat: category_colors.get(cat, 'gray') for cat in all_categories}

    # Plot
    plt.figure(figsize=(10, 8))
    ax = sns.lineplot(
        data=merged_df,
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
    plt.ylabel('Percentage of Earning (Income)', fontsize=22)
    plt.xticks(
        ticks=range(1, 13),
        labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        fontsize=14
    )
    plt.yticks(ticks=range(0, int(max(merged_df['percentage']))+2, 2), fontsize=14)
    plt.grid(axis='y')
    plt.tight_layout()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.legend(fontsize=20)
    st.pyplot(plt.gcf(), use_container_width=True)

    st.markdown(f"<h5 style='text-align: center; ;'>The sum of each category above should match the total spending in the right chart.</h5>", unsafe_allow_html=True)


