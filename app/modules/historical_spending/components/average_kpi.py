import streamlit as st
import pandas as pd

def average_kpi(year, expense, income, transaction):


    # --- 1. Calculations ---
    expense['date'] = pd.to_datetime(expense['date'])
    expense['month'] = expense['date'].dt.month
    unique_month = expense['month'].nunique()
    
    # Avoid division by zero
    divisor = unique_month if unique_month > 0 else 1

    # Financial Totals (Cast to float for math safety)
    total_income = float(income['total_income'].sum())
    total_expense = float(expense['amount'].sum())
    
    house_df = transaction[transaction['fund_category'] == 'House']
    house_sum = float(house_df['total_amount'].sum()) if not house_df.empty else 0.0
    
    total_spending = total_expense + house_sum

    # Helper function for data processing
    def get_stats(current_sum, total_inc, div):
        current_sum = float(current_sum)
        avg = current_sum / div
        pct = (current_sum / total_inc * 100) if total_inc > 0 else 0
        return current_sum, avg, pct

    # --- 2. Render Top Section (Headers, Totals, Averages) ---
    cols = st.columns(8)

    # Column 1: Row Labels
    with cols[0]:
        st.markdown(
            f"<p style='font-size: 20px; text-align: center;'><b>Category</b></p>"
            f"<p style='font-size: 22px; text-align: center; color: gray;'>Total Sum</p>"
            f"<p style='font-size: 22px; text-align: center; color: gray;'>Monthly Avg</p>",
            unsafe_allow_html=True,
        )

    # Data configuration for the categories
    categories = [
        {"name": "Earning", "color": "orange", "sum": total_income},
        {"name": "All Spending", "color": "#e74c3c", "sum": total_spending},
        {"name": "Daily", "color": "#f1c40f", "sum": expense[expense["summary_category"] == "Daily Expenses"]["amount"].sum()},
        {"name": "House", "color": "#bce784", "sum": house_sum},
        {"name": "Offerings", "color": "#989fce", "sum": expense[expense["summary_category"] == "Donation and Gifts"]["amount"].sum()},
        {"name": "Grocery", "color": "#ff8fab", "sum": expense[expense["category"] == "Grocery"]['amount'].sum()},
        {"name": "Retirement", "color": "#1AA7EC", "sum": transaction[(transaction['fund_category'] == 'Retirement Saving')]['total_amount'].sum()},
    ]

    # Render data for columns 2-8
    for i, cat in enumerate(categories):
        c_sum, c_avg, c_pct = get_stats(cat['sum'], total_income, divisor)
        categories[i]['pct'] = c_pct # Save for bottom row
        
        with cols[i+1]:
            st.markdown(
                f"<p style='font-size: 20px; color: {cat['color']}; text-align: center;'><b>{cat['name']}</b></p>"
                f"<p style='font-size: 22px; text-align: center;'>${c_sum:,.0f}</p>"
                f"<p style='font-size: 22px; text-align: center;'>${c_avg:,.0f}</p>",
                unsafe_allow_html=True,
            )

    # --- 3. The Whole-Width Dashed Line ---
    st.markdown("<hr style='margin: 0px; border: none; border-top: 2px dashed #bbb;'>", unsafe_allow_html=True)
    # --- 4. Render Bottom Section (% by Income) ---
    bcols = st.columns(8)

    with bcols[0]:
        st.markdown("<p style='font-size: 22px; text-align: center; font-weight: bold;'>% of Income</p>", unsafe_allow_html=True)

    for i in range(7):
        with bcols[i+1]:
            # Earning (index 0) is 100%, others use their calculated %
            display_pct = 100.0 if i == 0 else categories[i]['pct']
            st.markdown(f"<p style='font-size: 22px; text-align: center;'><b>{display_pct:.1f}%</b></p>", unsafe_allow_html=True)