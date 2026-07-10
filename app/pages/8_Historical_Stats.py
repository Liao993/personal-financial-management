from modules.historical_spending.middle_layer.selected_year_form import selected_year_choice_form
from modules.historical_spending.components.kpi import kpi
from modules.historical_spending.components.single_year_total_expense_by_category_bar_chart import create_summary_bar_chart
from modules.historical_spending.components.single_year_monthly_expense_by_category_bar_chart import create_monthly_expense_bar_chart
from modules.historical_spending.components.all_year_annual_expense_by_category_bar_chart import create_annual_expense_bar_chart
from modules.historical_spending.components.single_year_pct_monthly_expense_by_category_line_chart import create_expense_line_chart
from modules.historical_spending.components.all_year_pct_annual_expense_by_category_line_chart import create_annual_expense_percentage_chart
from modules.historical_spending.components.single_year_pct_saving_spending_distribution_line_chart import create_monthly_saving_spending_distribution_line_chart
from modules.historical_spending.components.all_year_pct_saving_spending_distribution_line_chart import create_annual_saving_spending_distribution_line_chart
from modules.historical_spending.components.all_year_total_expense_by_category_bar_chart import create_total_expense_distribution_chart

 
from backend import expense_backend, income_backend, transaction_backend
import pandas as pd # type: ignore
import streamlit as st # type: ignore

st.set_page_config(page_title="Historical Stats", page_icon="💰", layout="wide")


def fetch_all_annual_expense_safe():
    if hasattr(expense_backend, "fetch_all_annual_expense"):
        return expense_backend.fetch_all_annual_expense()

    conn = expense_backend.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT date, amount, category, summary_category
                FROM {expense_backend.DBT_SCHEMA}.intermediate_expenses_with_summary;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            return pd.DataFrame(rows, columns=cols)
        finally:
            cursor.close()
            conn.close()
    return pd.DataFrame()


def fetch_all_income_by_month_safe():
    if hasattr(income_backend, "fetch_all_income_by_month"):
        return income_backend.fetch_all_income_by_month()

    conn = income_backend.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT CAST(EXTRACT(YEAR FROM date) AS INTEGER) AS year,
                       CAST(EXTRACT(MONTH FROM date) AS INTEGER) AS month,
                       SUM(amount) AS amount
                FROM income
                GROUP BY 1, 2
                ORDER BY year, month;
            """
            cursor.execute(query)
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=["year", "month", "total_income"])
        finally:
            cursor.close()
            conn.close()
    return pd.DataFrame(columns=["year", "month", "total_income"])


def fetch_all_transaction_data_by_month_safe():
    if hasattr(transaction_backend, "fetch_all_transaction_data_by_month"):
        return transaction_backend.fetch_all_transaction_data_by_month()

    conn = transaction_backend.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT CAST(EXTRACT(YEAR FROM date) AS INTEGER) AS year,
                       CAST(EXTRACT(MONTH FROM date) AS INTEGER) AS month,
                       fund_category,
                       SUM(amount) AS total_amount
                FROM transactions
                WHERE transaction_type = 'Deposit'
                  AND source_notes LIKE %s
                  AND expense_id IS NULL
                GROUP BY 1, 2, fund_category
                ORDER BY year, month;
            """
            cursor.execute(query, ("saved from%",))
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=["year", "month", "fund_category", "total_amount"])
        finally:
            cursor.close()
            conn.close()
    return pd.DataFrame(columns=["year", "month", "fund_category", "total_amount"])


def fetch_all_transaction_data_by_year_safe():
    if hasattr(transaction_backend, "fetch_all_transaction_data_by_year"):
        return transaction_backend.fetch_all_transaction_data_by_year()

    conn = transaction_backend.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT fund_category, SUM(amount) AS total_amount
                FROM transactions
                WHERE expense_id IS NULL
                GROUP BY fund_category;
            """
            cursor.execute(query)
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=["fund_category", "total_amount"])
        finally:
            cursor.close()
            conn.close()
    return pd.DataFrame(columns=["fund_category", "total_amount"])



def historical_spending():

  
    selected_year = selected_year_choice_form()

    if selected_year is not None:
        is_all_year = selected_year == "All Year"
        if is_all_year:
            all_fetched_expense = fetch_all_annual_expense_safe()
            all_fetched_income = fetch_all_income_by_month_safe()
            all_fetched_transaction = fetch_all_transaction_data_by_year_safe() # Consider all transactions to reflect actual saving
            all_fetched_monthly_transaction = fetch_all_transaction_data_by_month_safe() # Only consider deposit
        else:
            all_fetched_expense = expense_backend.fetch_annual_expense(selected_year)
            all_fetched_income = income_backend.fetch_annual_income_by_month(selected_year)
            all_fetched_transaction = transaction_backend.fetch_transaction_data_by_year(selected_year) # Consider all transactions to reflect actual saving
            all_fetched_monthly_transaction = transaction_backend.fetch_transaction_data_by_month(selected_year) # Only consider deposit
        if (len(all_fetched_expense) == 0) | (len(all_fetched_income) == 0):
            st.warning("No Spending or Annual Income in the selected period")
            #if st.button("Choose Again", key="choose_again"):
             #   selected_year_choice_form()
        else:
            kpi(all_fetched_expense, all_fetched_income, all_fetched_transaction, all_year=is_all_year)
            col1, col2 = st.columns(2)
            with col1:
                 # Show All Monthly Expenses by Amount
                if is_all_year:
                    create_annual_expense_bar_chart(all_fetched_expense, all_fetched_monthly_transaction)
                else:
                    create_monthly_expense_bar_chart(all_fetched_expense, all_fetched_monthly_transaction)
                
            with col2:
                # Show All Monthly Expenses by Percentage
                if is_all_year:
                    create_annual_expense_percentage_chart(all_fetched_expense, all_fetched_income, all_fetched_monthly_transaction)
                else:
                    create_expense_line_chart(all_fetched_expense, all_fetched_income, all_fetched_monthly_transaction)
                
            col3, col4 = st.columns(2)
                
            with col3:
                # Show All Expense Category Annually 
                if is_all_year:
                    create_total_expense_distribution_chart(all_fetched_expense)
                else:
                    create_summary_bar_chart(all_fetched_expense)
            with col4:
                #Spending vs Saving Distribution
                if is_all_year:
                    create_annual_saving_spending_distribution_line_chart(all_fetched_expense, all_fetched_income, all_fetched_monthly_transaction)
                else:
                    create_monthly_saving_spending_distribution_line_chart(all_fetched_expense, all_fetched_income, all_fetched_monthly_transaction)
if __name__ == "__main__":
    historical_spending()
