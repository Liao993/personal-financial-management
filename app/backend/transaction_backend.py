import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore

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
               fund_category, source_notes, transfer_to_account,
               transfer_to_fund_category
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
             """
            values = (
                validated_data['date'],
                validated_data['account_name'],
                validated_data['transaction_type'],
                validated_data['amount'],
                validated_data['fund_category'],
                validated_data['source_notes'],
                validated_data['transfer_to_account'],
                validated_data['transfer_to_fund_category'],
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


