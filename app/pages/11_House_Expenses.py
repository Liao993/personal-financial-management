import streamlit as st # type: ignore
import pandas as pd

from backend.expense_backend import fetch_house_expesne
st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def house_expenses():
    st.markdown("<h1 style='text-align: center;'>House Expenses</h1>", unsafe_allow_html=True)
    data = fetch_house_expesne()
    st.table(data)

if __name__ == "__main__":
  house_expenses()
 