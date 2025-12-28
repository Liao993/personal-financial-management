import streamlit as st # type: ignore
import pandas as pd

from backend.expense_backend import fetch_house_expesne
from backend.transaction_backend import fetch_all_transaction_data
from modules.house_expenses.components.annual_expense_by_category import create_category_bar_chart
from modules.house_expenses.components.annual_expense_by_summary import create_summary_category_chart
from modules.house_expenses.components.kpi import annual_kpi
st.set_page_config(page_title="Hose Expenses", page_icon="💰", layout="wide")


def house_expenses():

    house_expense_data = fetch_house_expesne()
    columns_names, all_trensaction_data = fetch_all_transaction_data()
    annual_kpi(house_expense_data, all_trensaction_data)
    col1, col2 = st.columns(2)
    with col1:
      create_summary_category_chart(house_expense_data)
    with col2:
      create_category_bar_chart(house_expense_data)
    st.table(house_expense_data)
if __name__ == "__main__":
  house_expenses()
 