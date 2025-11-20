import streamlit as st # type: ignore
import pandas as pd # type: ignore
from backend.transaction_backend import fetch_all_transaction_data
from utils.data import years
from modules.current_saving.component.Pivot_Table import Pivot_Table
from modules.current_saving.component.Account_Sum import Account_Sum
from modules.current_saving.component.Saving_Sum import saving_sum
st.set_page_config(page_title="Current_Status", page_icon="💰", layout="wide")


def current_saving_status():
    today_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    st.markdown(f"<h1 style='color: #ffffff; text-align: center;'>Fund Distribution by Account and Category - {today_date} </h1>", unsafe_allow_html=True)
    columns_names , all_data = fetch_all_transaction_data()
    original_data = pd.DataFrame(all_data, columns=columns_names)

    Account_Sum(original_data)

    Pivot_Table(original_data)


    st.write("___")

    saving_sum(original_data)
    
if __name__ == "__main__":
    current_saving_status()