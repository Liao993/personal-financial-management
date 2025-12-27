import streamlit as st # type: ignore
import pandas as pd

from backend.expense_backend import fetch_house_expesne
from modules.house_expenses.components.annual_expense_by_category import create_category_bar_chart
from modules.house_expenses.components.annual_expense_by_summary import create_summary_category_chart
st.set_page_config(page_title="Hose Expenses", page_icon="💰", layout="wide")


def house_expenses():
    st.markdown("<h1 style='text-align: center;'>House Expenses</h1>", unsafe_allow_html=True)

    data = fetch_house_expesne()
   
    col1, col2 = st.columns(2)
    with col1:
      create_summary_category_chart(data)
    with col2:
      create_category_bar_chart(data)
    st.table(data)
if __name__ == "__main__":
  house_expenses()
 