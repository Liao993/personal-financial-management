import streamlit as st # type: ignore
import pandas as pd
import sys
from pathlib import Path

# Add parent dir to path
sys.path.append(str(Path(__file__).parents[2]))

from etl.house_pipeline import run_house_etl
st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def house_expenses():
    st.markdown("<h1 style='text-align: center;'>House Expenses</h1>", unsafe_allow_html=True)
    data = run_house_etl()
    st.table(data)

if __name__ == "__main__":
  house_expenses()
 