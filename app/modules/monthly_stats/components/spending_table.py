import streamlit as st # type: ignore
import pandas as pd

def display_spending_table(monthly_expense_daily_data, monthly_income):
    # Expense by Summary Category
    spending_by_summary = monthly_expense_daily_data.groupby('summary_category')['amount'].sum().reset_index()
    spending_by_summary.rename(columns={'summary_category': 'Summary Category', 'amount': 'Amount'}, inplace=True)
    spending_by_summary['Amount'] = spending_by_summary['Amount'].astype(float)

    # Calculate Total Expense
    total_expense = spending_by_summary['Amount'].sum()

    st.markdown(f"<h3 style='text-align: center;'>Spending Breakdown - Total Expense: <span style='color: #8B0000; font-size: 28px; font-weight: bold;'>${total_expense:.2f}</span></h3>", unsafe_allow_html=True)
    st.write("")
    if monthly_income > 0:
        spending_by_summary['Percentage (of Income)'] = (spending_by_summary['Amount'] / monthly_income) * 100
        spending_by_summary['Percentage (of Income)'] = spending_by_summary['Percentage (of Income)'].map('{:.2f}%'.format)
    else:
        spending_by_summary['Percentage (of Income)'] = 'N/A'

    spending_by_summary['Amount'] = spending_by_summary['Amount'].map('${:.2f}'.format)

    # Display the spending breakdown table
    st.table(spending_by_summary.set_index('Summary Category'))
