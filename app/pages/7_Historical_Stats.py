from modules.historical_spending.middle_layer.selected_year import selected_year_choice
from modules.historical_spending.components.annual_kpi import annual_kpi
from modules.historical_spending.components.bar_chart import create_summary_bar_chart
from modules.historical_spending.components.line_expense_chart import create_expense_line_chart
from modules.historical_spending.components.line_monthly_chart import create_monthly_line_chart
from backend.expense_backend import fetch_annual_expense
from backend.income_backend import fetch_annual_income_by_month
from backend.transaction_backend import fetch_transaction_data_by_month
import streamlit as st # type: ignore

st.set_page_config(page_title="Historical Stats", page_icon="💰", layout="wide")

edit_mode = 'regular_edit_mode'
year_select_key = "year_select"
def historical_spending():
    if edit_mode not in st.session_state:
        st.session_state[edit_mode] = True

    selected_year = None

    if st.session_state[edit_mode]:
        st.markdown("<h1 style='color: orange; text-align: center;'>Historical Stats</h1>", unsafe_allow_html=True)
        selected_year_choice(key=year_select_key)  # Pass the key
        if st.button("Submit", key="submit_year"):
            st.session_state[edit_mode] = False
            st.rerun()

    else:
        selected_year = st.session_state.get(year_select_key)  # Access using the key


        if selected_year is not None:
            all_fetched_expense = fetch_annual_expense(selected_year)
            all_fetched_income = fetch_annual_income_by_month(selected_year)
            all_fetched_transaction = fetch_transaction_data_by_month(selected_year)

            if (len(all_fetched_expense) == 0) | (len(all_fetched_income) == 0):
                st.warning("No Spending or Annual Income in the selected year")
                if st.button("Choose Again", key="choose_again"):
                    st.session_state[edit_mode] = True
                    st.rerun()
            else:
                annual_kpi(all_fetched_expense, selected_year, all_fetched_income)
                col1, col2 = st.columns(2)
                with col1:
                    create_summary_bar_chart(all_fetched_expense)
                with col2:
                    create_expense_line_chart(all_fetched_expense, all_fetched_income)
                
                create_monthly_line_chart(all_fetched_expense, all_fetched_income, all_fetched_transaction)
if __name__ == "__main__":
    historical_spending()