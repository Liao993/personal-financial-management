import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore
import os
DBT_SCHEMA = os.environ.get("DBT_SCHEMA", "dbt_budget")
def fetch_trip_selection():
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
         
            query = f"""
                        SELECT DISTINCT 
                            trip, 
                            TO_DATE(SPLIT_PART(trip, '-', 2), 'MMYYYY') as sort_date
                        FROM {DBT_SCHEMA}.intermediate_expenses_with_summary
                        WHERE category = 'Traveling'
                        ORDER BY sort_date DESC;
                    """
            cursor.execute(query, ())

            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            data = df[cols]
            return data

        except psycopg2.Error as e:
            st.error(f"Error retrieving trip data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()



def fetch_trip_expense(trip):
    """Fetches annual expense data from the database."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
         # To calculate total_spending by trip and the % for category in SQL first
        query = f"""
                SELECT
                    trip,
                    traveling_category,
                    SUM(amount) AS category_spending,
                    ROUND(SUM(amount_I_spend),2) AS category_i_spent,
                    SUM(SUM(amount)) OVER (PARTITION BY trip) AS total_spending,
                    ROUND(SUM(SUM(amount_I_spend)) OVER (PARTITION BY trip),2) AS total_i_spent,
                    -- Percentage of Total (Safe from Division by Zero)
                    ROUND(
                        (SUM(amount) / NULLIF(SUM(SUM(amount)) OVER (PARTITION BY trip), 0)) * 100.0, 
                    2) AS percentage_total,
                    
                    -- Percentage I Spent (Safe from Division by Zero)
                    ROUND(
                        (SUM(amount_I_spend) / NULLIF(SUM(SUM(amount_I_spend)) OVER (PARTITION BY trip), 0)) * 100.0, 
                    2) AS percentage_I_spent
                FROM
                    {DBT_SCHEMA}.intermediate_expenses_with_summary
                WHERE
                    category = 'Traveling' AND trip = %s 
                GROUP BY
                    trip,
                    traveling_category
                ORDER BY
                    trip,
                    traveling_category;

            """
        try:
            cursor.execute(query, (trip,))
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()