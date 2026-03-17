import streamlit as st # type: ignore
import pandas as pd
import subprocess
import datetime

from backend.expense_backend import fetch_house_expesne
from backend.transaction_backend import fetch_all_transaction_data
from modules.house_expenses.components.annual_expense_by_category import create_category_bar_chart
from modules.house_expenses.components.annual_expense_by_summary import create_summary_category_chart
from modules.house_expenses.components.kpi import annual_kpi

st.set_page_config(page_title="House Expenses", page_icon="💰", layout="wide")


def house_expenses():
    # Initialize session state for last update time
    if 'last_house_update' not in st.session_state:
        st.session_state.last_house_update = "Never"

    col_title, col_btn = st.columns([3, 1])
    
    with col_title:
        st.title("House Expenses")
    
    with col_btn:
        st.write("") # some spacing
        if st.button("🔄 Sync House Data", use_container_width=True):
            with st.spinner("Syncing data with Google Sheets..."):
                try:
                    # Run the pipeline command internally inside the budget_streamlit container
                    result = subprocess.run(
                        ["python", "/etl/house_pipeline.py"], 
                        capture_output=True, 
                        text=True, 
                        check=True
                    )
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.last_house_update = now
                    st.success(f"Data synced successfully!")
                    st.rerun()
                except subprocess.CalledProcessError as e:
                    st.error(f"Error syncing data: {e.stderr}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
            
        st.markdown(f"<p style='font-size: 12px; color: gray; text-align: right;'>Last Updated: {st.session_state.last_house_update}</p>", unsafe_allow_html=True)

    st.divider()

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