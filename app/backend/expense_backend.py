import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore

def insert_expense_data(validated_data: dict):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO expense (date, items, amount, category, traveling_category) VALUES (%s, %s, %s, %s, %s)"
            #  validated_data['traveling_category'] can be None
            values = (
                validated_data['date'],
                validated_data['items'],
                validated_data['amount'],
                validated_data['category'],
                validated_data.get('traveling_category'),  # Use .get() to handle missing key
            )
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


def fetch_annual_expense(year):
    """Fetches annual expense data from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
         
            if isinstance(year, int):
                query = """
                    SELECT date, amount, category, summary_category
                    FROM dbt_budget.intermediate_expenses_with_summary
                    WHERE EXTRACT(YEAR FROM date) = %s AND category != 'Traveling'
                """
                cursor.execute(query, (year,))
            else:
                st.error("Invalid year format.  Please select a valid year.")
                return pd.DataFrame()

            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()

def fetch_trip_list():
   
    """
    Fetches the unique values from a specified column in a database table.

    Args:
        conn (psycopg2.connection): A database connection object.
        table_name (str): The name of the table.
        column_name (str): The name of the column.

    Returns:
        list: A list of unique values from the column, or an empty list on error.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = f"SELECT DISTINCT trip FROM expense"
            cursor.execute(query)
            unique_values = [row[0] for row in cursor.fetchall()]  # Fetch and extract values
            cursor.close()
            return unique_values
        except psycopg2.Error as e:
            st.error(f"Error fetching unique values: {e}")
            if cursor:
                cursor.close()
            return []