import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd

def insert_transaction_data(validated_data: dict):
    #st.info("Received validated income data in income_backend.py:")
    # Here you would add your logic to interact with the database
    # using the validated_data (e.g., insert into the income table)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        success = False
        try:
            query = """
            INSERT INTO transactions (
               date, account_name, transaction_type, amount,
               fund_category, source_notes, transfer_to_account
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
             """
            values = (
                validated_data['date'],
                validated_data['account_name'],
                validated_data['transaction_type'],
                validated_data['amount'],
                validated_data['fund_category'],
                validated_data['source_notes'],
                validated_data['transfer_to_account']
            )
            cursor.execute(query, values)
            conn.commit()
            success = True
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting transaction data: {e}")
        finally:
            cursor.close()
            conn.close()
        return success
    else:
        st.info("Database connection failed, cannot insert data.")
        return False



def fetch_all_transaction_data():
    # Here you would add your logic to retrieve data from the database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT *
        FROM transactions
        """
        try:
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description] 
            result = cursor.fetchall()  # Use fetchall() to get all rows
            return column_names, result  # Return all the rows
            
        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []


def fetch_transaction_deposit_check(year, month):
    # Here you would add your logic to retrieve data from the database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT date, fund_category, amount
        FROM transactions
        WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s AND transaction_type = 'Deposit';
        """
        try:
            cursor.execute(query, (year, month))
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            return df
            
        except psycopg2.Error as e:
            st.error(f"Error retrieving transaction data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []