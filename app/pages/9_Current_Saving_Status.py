import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data
from utils.data import years
from modules.current_saving.component.Pivot_Table import Pivot_Table
from modules.current_saving.component.Retirement import Retirement
from modules.current_saving.component.Medium import Medium_Term
from modules.current_saving.component.Account_Sum import Account_Sum
st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def current_saving_status():
    today_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    st.markdown(f"<h1 style='color: #ffffff; text-align: center;'>Fund Distribution by Account and Category - {today_date} </h1>", unsafe_allow_html=True)
    columns_names , all_data = fetch_all_transaction_data()
    original_data = pd.DataFrame(all_data, columns=columns_names)

    Account_Sum(original_data)

    Pivot_Table(original_data)

    

    st.write("___")
    col1, col2 = st.columns(2)
    
    selected_year = st.selectbox("Select Year", years) # type: ignore
    with col1:
        Retirement(selected_year, original_data)
    with col2:
        Medium_Term(selected_year, original_data)
    
if __name__ == "__main__":
    current_saving_status()