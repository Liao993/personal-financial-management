import streamlit as st

def calculate_spending_percentages(spending_data, total_income):
    """Calculates the percentage of total income for each spending category."""
    spending_percentages = {}
    if total_income > 0:
        for cat, val in spending_data.items():
            spending_percentages[cat] = round((val / total_income) * 100, 2)
    return spending_percentages