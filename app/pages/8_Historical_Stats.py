from modules.historical_spending.middle_layer.selected_year_form import selected_year_choice_form
from modules.historical_spending.components.annual_kpi import annual_kpi
from modules.historical_spending.components.expense_summary_chart import create_summary_bar_chart
from modules.historical_spending.components.expense_category_pct_chart import create_expense_line_chart
from modules.historical_spending.components.saving_spending_balance_chart import create_monthly_saving_spending_distribution_line_chart
from modules.historical_spending.components.monthly_expense_chart import create_monthly_expense_bar_chart
 
from backend.expense_backend import fetch_annual_expense
from backend.income_backend import fetch_annual_income_by_month
from backend.transaction_backend import fetch_transaction_data_by_month
import streamlit as st # type: ignore

st.set_page_config(page_title="Historical Stats", page_icon="💰", layout="wide")



def historical_spending():

  
    selected_year = selected_year_choice_form()


    if selected_year is not None:
        all_fetched_expense = fetch_annual_expense(selected_year)
        all_fetched_income = fetch_annual_income_by_month(selected_year)
        all_fetched_transaction = fetch_transaction_data_by_month(selected_year)

        if (len(all_fetched_expense) == 0) | (len(all_fetched_income) == 0):
            st.warning("No Spending or Annual Income in the selected year")
            #if st.button("Choose Again", key="choose_again"):
             #   selected_year_choice_form()
        else:
            annual_kpi(all_fetched_expense, selected_year, all_fetched_income, all_fetched_transaction)
            col1, col2 = st.columns(2)
            with col1:
                create_summary_bar_chart(all_fetched_expense)
            with col2:
                create_monthly_expense_bar_chart(all_fetched_expense)
                
            col3, col4 = st.columns(2)
                
            with col3:
                create_expense_line_chart(all_fetched_expense, all_fetched_income)
            with col4:
                create_monthly_saving_spending_distribution_line_chart(all_fetched_expense, all_fetched_income, all_fetched_transaction)
if __name__ == "__main__":
    historical_spending()