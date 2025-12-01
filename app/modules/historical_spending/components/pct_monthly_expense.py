import streamlit as st  # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

def create_expense_line_chart(expense, income, transaction):
    
   

    st.markdown(f"<h3 style='text-align: center; color: #16a085;'>Percentage of Expense by Category by Month</h3>", unsafe_allow_html=True)
    
    # Extract the month from the 'date' column
    expense['date'] = pd.to_datetime(expense['date'])
    expense['month'] = expense['date'].dt.month

    # Filter for the specified categories
    categories_of_interest = ['Grocery', 'Food Outside', 'Donation', 'Gas', "Gifts", 'Education', "Exercise"]
    expense['major_category'] = expense['category'].apply(lambda x: x if x in categories_of_interest else 'Others')

    # Group data
    grouped = (
        expense.groupby(['month', 'major_category'], as_index=False)['amount']
        .sum()
        .rename(columns={'amount': 'total_amount'})
    )

    # add house amount
    house = transaction[transaction['fund_category'] == 'House']
    house.rename(columns={'fund_category': 'major_category', "total_amount": "total_amount"}, inplace=True)
    grouped = pd.concat([grouped, house], ignore_index=True)
    
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
        'Grocery': '#5dade2',
        'Food Outside': "#e0a539",
        'Gas': "#198553A0",
        'Donation': "#e62922",
        'Others': "#716E74",
        'Gifts': "#BD1CC5",
        'Education': "#130fe4",
        'Exercise': "#07294b"

    }
    palette = {cat: category_colors.get(cat, 'gray') for cat in all_categories}

    # a. Filter data for the main line plot (excluding 'House')
    df_plot = merged_df[merged_df['major_category'] != 'House'].copy()

    # b. Extract data for the House percentage table
    df_house = merged_df[merged_df['major_category'] == 'House'].copy()

    # c. Pivot and re-index House data to ensure all 12 months (1-12) are present
    house_pivot = (
        df_house.set_index('month')['percentage']
        .reindex(range(1, 13), fill_value=0) # Fill missing months with 0%
    )
    # d. Format the percentage data for the table row
    # The data needs to be a list of lists: [[value_Jan, value_Feb, ...]]
    house_percentages_formatted = [f"{p:.1f}%" for p in house_pivot.tolist()]
    house_table_data = [house_percentages_formatted] 

    # Plot
    plt.figure(figsize=(10, 7.75))
    ax = sns.lineplot(
        data=df_plot,
        x='month',
        y='percentage',
        hue='major_category',
        palette=palette,
        marker='o',
        linewidth=3,
        markersize=8,
        dashes=False
    )
    # Make room at the bottom of the plot area for the table
    plt.subplots_adjust(bottom=0.25) 

    # Add the table to the axis
    month_labels = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

    table = ax.table(
        cellText=house_table_data,
        rowLabels=['House %'],
        colLabels=month_labels, # Use month abbreviations as column headers for the table
        cellLoc='center',
        loc='bottom',
        # Place the table below the existing x-axis labels
        # [left, bottom, width, height]
        bbox=[0.05, -0.25, 0.9, 0.1]
    )

     # Formatting the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(month_labels))))

    # Style cells (set font weight/color/background)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#cccccc')
        if row == 0: # Column Headers
            cell.set_facecolor('#f5f5f5')
            cell.set_text_props(weight='bold')
        elif col == -1: # Row Label 'House %'
            cell.set_facecolor(category_colors.get('House', "#1eb23297")) # Use the House color
            cell.set_text_props(weight='bold', color='black')
        else: # Data cells
            cell.set_facecolor('white')

    # 4. FINALIZING THE PLOT APPEARANCE       

    plt.title(f'Avg. Monthly Income: ${monthly_income:.2f}', loc='right', fontsize=20)
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Percentage of Earning (Income)', fontsize=22)
    plt.xticks(
        ticks=range(1, 13),
        labels=month_labels,
        fontsize=14
    )
    plt.yticks(ticks=range(0, int(max(df_plot['percentage']))+2, 2), fontsize=14)
    plt.grid(axis='y')
    plt.tight_layout()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.legend(
    fontsize=16,
    ncol=3
    )

    st.pyplot(plt.gcf(), use_container_width=True)

    st.markdown(f"<h5 style='text-align: center; ;'>The sum of each category above should match the total spending in the below chart.</h5>", unsafe_allow_html=True)


