import streamlit as st  # type: ignore
import pandas as pd  # type: ignore

from utils.data import years
from backend.expense_backend import fetch_annual_expense
from backend.income_backend import fetch_annual_income_by_month
from backend.transaction_backend import fetch_transaction_data_by_year


def render_historical_kpi_section():
    st.subheader("📅 Historical KPI")

    current_year = pd.Timestamp.now().year
    default_index = years.index(current_year) if current_year in years else 0
    selected_year = st.selectbox("Year", years, index=default_index, key="mobile_kpi_year")

    expense = fetch_annual_expense(selected_year)
    income = fetch_annual_income_by_month(selected_year)
    transaction = fetch_transaction_data_by_year(selected_year)

    if expense.empty or income.empty:
        st.info(f"No spending or income data recorded for {selected_year} yet.")
        return

    total_income = float(income["total_income"].sum())
    total_expense = float(expense["amount"].sum())

    house_df = transaction[transaction["fund_category"] == "House"]
    house_sum = float(house_df["total_amount"].sum()) if not house_df.empty else 0.0
    total_spending = total_expense + house_sum

    daily = float(expense[expense["summary_category"] == "Daily Expenses"]["amount"].sum())
    offerings = float(
        expense[expense["summary_category"] == "Donation and Gifts"]["amount"].sum()
    )
    grocery = float(expense[expense["category"] == "Grocery"]["amount"].sum())

    retirement_df = transaction[transaction["fund_category"] == "Retirement Saving"]
    retirement = float(retirement_df["total_amount"].sum()) if not retirement_df.empty else 0.0

    def pct(part):
        return (part / total_income * 100) if total_income > 0 else 0.0

    # (label, amount, % of income) — mirrors the desktop Historical Stats
    # KPI row (app/modules/historical_spending/components/kpi.py), minus
    # the monthly-average row, to keep this to one screen on a phone.
    rows = [
        ("Earning", total_income, 100.0),
        ("All Spending", total_spending, pct(total_spending)),
        ("Daily", daily, pct(daily)),
        ("House", house_sum, pct(house_sum)),
        ("Offerings", offerings, pct(offerings)),
        ("Grocery", grocery, pct(grocery)),
        ("Retirement", retirement, pct(retirement)),
    ]

    for i in range(0, len(rows), 2):
        row_pair = rows[i : i + 2]
        cols = st.columns(len(row_pair))
        for col, (label, amount, percentage) in zip(cols, row_pair):
            with col:
                # No delta/arrow here on purpose — "% of income" is a static
                # ratio, not a trend, so st.metric's up/down arrow (which
                # shows even with delta_color="off", just in gray) would be
                # misleading. Plain caption instead, no icon, no color.
                st.metric(label, f"${amount:,.0f}")
                st.caption(f"{percentage:.1f}% of income")