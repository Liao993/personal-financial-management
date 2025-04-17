import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore

def insert_expense_data(validated_data: dict):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO expense (date, items, amount, category) VALUES (%s, %s, %s, %s)"
            values = (validated_data['date'], validated_data['items'], validated_data['amount'], validated_data['category'])
            cursor.execute(query, values)
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting expense data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot insert data.")

# Get Montlhy Expenses by Summary Category
def fetch_monthly_expenses_with_summary(year, month):

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT date, amount, category, summary_category
        FROM dbt_budget.intermediate_expenses_with_summary
        WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s;
        """
        try:
            cursor.execute(query, (year, month))
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            return df
        except psycopg2.Error as e:
            st.error(f"Error fetching monthly expenses with summary: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.error("Database connection failed, cannot fetch expense data.")
        return pd.DataFrame()
