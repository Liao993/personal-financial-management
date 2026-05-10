import streamlit as st # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import numpy as np # type: ignore
import decimal

def create_monthly_expense_bar_chart(expense, transaction):
    st.markdown("<h3 style='text-align: center; color: orange;'>Monthly Expense by Category</h3>", unsafe_allow_html=True)

    
    expense['month'] = pd.to_datetime(expense['date']).dt.month
    
    # 1. REFRACTOR CATEGORIZATION: Define the three groups
    def categorize_expense(category):
        if category == 'Donation':
            return 'Donation'
        elif category == 'Grocery':
            return 'Grocery'
        elif category == 'Gifts':
            return 'Gifts'
        elif category == 'Car':
            return 'Car & Gas'
        elif category == 'Gas':
            return 'Car & Gas'
        else:
            return 'Other'
            
    expense['expense_group'] = expense['category'].apply(categorize_expense)
    

    # 1. Aggregate donation and non-donation amounts separately by month
    summary_data = (
    expense.groupby(['month', 'expense_group'])['amount']
    .sum()
    .reset_index()
    )

    # 2. add House amount
    house = transaction[transaction['fund_category'] == 'House']
    house.rename(columns={'fund_category': 'expense_group', "total_amount": "amount"}, inplace=True)
    summary_data = pd.concat([summary_data, house], ignore_index=True)

    # Convert Decimal to float
    summary_data['amount'] = summary_data['amount'].apply(decimal.Decimal.__float__)
    # 3.Pivot so each month has two columns: Donation, Grocery, Others
    pivot_data = summary_data.pivot(index='month', columns='expense_group', values='amount').fillna(0)
    # Ensure all three columns exist, even if a month has 0 for a category
    required_cols = ['Grocery', 'Other', 'Donation', "Gifts", "House", "Car & Gas"]
    for col in required_cols:
        if col not in pivot_data.columns:
            pivot_data[col] = 0

    # Extract columns (Note: order matters for stacking)
    months = pivot_data.index
    grocery = pivot_data['Grocery']
    other = pivot_data['Other']
    donation = pivot_data['Donation']
    gifts = pivot_data['Gifts']
    house = pivot_data['House']
    car = pivot_data['Car & Gas']


    #5. Calculate the 'bottom' positions for stacking
    #The order from the lowest to the top
    lowest = house
    second_lowest = grocery + house
    third_lowest = grocery + house + other
    fourth_lowest = grocery + house + other + car
    fifth_lowest = grocery + house + car + other + donation

    # 6. Plot stacked bar chart (using the specified colors and order)
    plt.figure(figsize=(10, 8))

    # Bar 1:  House (Second Bottom) - green
    plt.bar(months, house, color='green', label='House')
    
    # Bar 2: Grocery (Bottom) - pink
    plt.bar(months, grocery, bottom=lowest, color='#ff8fab', label='Grocery')
    
    # Bar 3: Other (Third Bottom) - orange
    plt.bar(months, other, bottom=second_lowest, color='orange', label='Other')

    # Bar 4: Car (Fourth Bottm) - lightblue
    plt.bar(months, car, bottom=third_lowest, color='lightblue', label='Car & Gas')
    # Bar 5: Donation (Fifth Bottom) - red
    plt.bar(months, donation, bottom=fourth_lowest, color='red', label='Donation')



    # Bar 5: Gifts (Top) - purple
    plt.bar(months, gifts, bottom=fifth_lowest, color='purple', label='Gifts')

    # Labels
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Amount', fontsize=18)

    # Y-Axis ticks (every 100)
    max_amt = (fifth_lowest + gifts).max()
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

   

