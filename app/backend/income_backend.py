import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore



def process_income_data(validated_data: dict):
    #st.info("Received validated income data in income_backend.py:")
    # Here you would add your logic to interact with the database
    # using the validated_data (e.g., insert into the income table)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO income (date, amount, source, regular)
                VALUES (%s, %s, %s, %s)
                """,
                (validated_data['date'], validated_data['amount'], validated_data['source'], validated_data['regular']),
            )
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting income data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot insert data.")
