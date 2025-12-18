import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore

def insert_cashflow_data(validated_data: dict):
    #st.info("Received validated income data in income_backend.py:")
    # Here you would add your logic to interact with the database
    # using the validated_data (e.g., insert into the income table)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        success = False
        try:
            query = """
            INSERT INTO cashflow (
               date, account_name, transaction_type, amount,
               purpose, source_notes, transfer_to_account
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
             """
            values = (
                validated_data['date'],
                validated_data['account_name'],
                validated_data['transaction_type'],
                validated_data['amount'],
                validated_data['purpose'],
                validated_data['source_notes'],
                validated_data['transfer_to_account']
            )
            cursor.execute(query, values)
            conn.commit()
            success = True
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting cashflow transaction data: {e}")
        finally:
            cursor.close()
            conn.close()
        return success
    else:
        st.info("Database connection failed, cannot insert cashflow data.")
        return False



def fetch_transaction_data_by_account_by_month():
    # Here you would add your logic to retrieve data from the database
    conn = get_db_connection()
    #search_pattern = "saved from%" AND source_notes LIKE %s
    if conn:
        cursor = conn.cursor()
        query = """
            WITH total_amount_by_month AS (
                SELECT EXTRACT(MONTH FROM date) AS month, SUM(amount) AS monthly_savings
                FROM cashflow
                GROUP BY EXTRACT(MONTH FROM date)
            )
            SELECT EXTRACT(MONTH FROM date) AS month, account_name, SUM(amount) AS total_amount, t.monthly_savings
            FROM cashflow as c JOIN total_amount_by_month as t ON EXTRACT(MONTH FROM date) = t.month
            WHERE
                date>= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                AND date < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
            GROUP BY EXTRACT(MONTH FROM date), account_name, t.monthly_savings
            ORDER BY month;  -- Order by month for consistency
            """
        try:
            cursor.execute(query, ())
            columns = ['month', 'account_name', 'total_amount', 'monthly_savings']  # Define column names
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=columns) # return empty df
            
        except psycopg2.Error as e:
            st.error(f"Error retrieving cashflow transaction data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []



def fetch_all_transaction_data():
    """
    Fetches all data from the transactions table.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing all transaction data,
                      or an empty DataFrame if no data is found or an error occurs.
                      Returns None if the database connection fails.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT *
            FROM transactions
            """
        try:
            cursor.execute(query) #removed the extra parameter
            columns = [desc[0] for desc in cursor.description] #added this line to get the column names
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=columns) # Pass the column names to the DataFrame constructor
                return columns, df
            else:
                return pd.DataFrame()  # Return empty DataFrame
        except psycopg2.Error as e:
            st.error(f"Error retrieving transaction data: {e}")
            return columns, None # Return None on error
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return columns, None  # Return None on connection failure


def fetch_last_cashflow_data():
    """Fetches the last two transaction data from the database."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT *
            FROM cashflow
            ORDER BY date DESC
            LIMIT 20;
        """
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=columns)
                return df
            else:
                return pd.DataFrame()  # Return empty DataFrame if no data found
        except psycopg2.Error as e:
            st.error(f"Error retrieving last cashflow data: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve last cashflow data.")
        return pd.DataFrame()  # Return empty DataFrame on connection failure