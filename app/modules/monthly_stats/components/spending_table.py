import streamlit as st
import pandas as pd
from utils.calculation.incomeDistribution import calculate_spending_percentages # type: ignore

def display_spending_table(spending_data, monthly_income):
    """Displays the spending breakdown table."""
    st.markdown("<h3 style='text-align: center;'>Spending Breakdown</h3>", unsafe_allow_html=True)
    spending_percentages = calculate_spending_percentages(spending_data, monthly_income)

    spending_table_data = []
    for category, amount in spending_data.items():
        spending_table_data.append({
            "Category": category,
            "Amount": f"${amount:.2f}",
            "Percentage (of Income)": f"{spending_percentages.get(category, 0.0):.2f}%"
        })

    spending_df = pd.DataFrame(spending_table_data)
    st.table(spending_df)