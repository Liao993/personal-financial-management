import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore

def insert_expense_data(validated_data: dict):
    #st.info("Received validated income data in income_backend.py:")
    # Here you would add your logic to interact with the database
    # using the validated_data (e.g., insert into the income table)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO expense (date, items, amount, category)
                VALUES (%s, %s, %s, %s)
                """,
                (validated_data['date'], validated_data['items'], validated_data['amount'], validated_data['category']),
            )
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting expense data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot insert data.")
