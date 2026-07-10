import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore
def insert_income_data(validated_data: dict):
    #st.info("Received validated income data in income_backend.py:")
    # Here you would add your logic to interact with the database
    # using the validated_data (e.g., insert into the income table)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO income (date, amount, source, regular, notes) VALUES (%s, %s, %s, %s, %s)"
            values = (
                validated_data['date'],
                validated_data['amount'],
                validated_data['source'],
                validated_data['regular'],
                validated_data['notes']
            )
            cursor.execute(query, values)
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting income data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot insert data.")

def fetch_annual_income_by_month(year):
    # Here you would add your logic to retrieve data from the database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT EXTRACT(MONTH FROM date) AS month, SUM(amount) As amount
            FROM income
            WHERE EXTRACT(YEAR FROM date) = %s
            GROUP BY EXTRACT(MONTH FROM date)
            ORDER BY month;  -- Order by month for consistency
    """
        try:
            cursor.execute(query, (year,))
            columns = ['month', 'total_income']  # Define column names
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=columns) # return empty df
            
        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []


def fetch_all_income_by_month():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT CAST(EXTRACT(YEAR FROM date) AS INTEGER) AS year,
                   CAST(EXTRACT(MONTH FROM date) AS INTEGER) AS month,
                   SUM(amount) AS amount
            FROM income
            GROUP BY 1, 2
            ORDER BY year, month;
        """
        try:
            cursor.execute(query)
            columns = ["year", "month", "total_income"]
            data = cursor.fetchall()
            if data:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame(columns=columns)
        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return pd.DataFrame(columns=["year", "month", "total_income"])
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame(columns=["year", "month", "total_income"])

def fetch_monthly_income(year, month):
    # Here you would add your logic to retrieve data from the database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT SUM(amount)
        FROM income
        WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s;
    """
        try:
            cursor.execute(query, (year, month))
            result = cursor.fetchone()
            if result and result[0] is not None:
                return float(result[0])
            else:
                return 0.0
            
        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []

def fetch_last_income_data():
    """Fetches the last income data from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT date, amount, source, notes
                FROM income
                ORDER BY date DESC
                LIMIT 20;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving last two income data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
