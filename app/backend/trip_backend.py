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
         
            query = """
                        SELECT DISTINCT 
                            trip, 
                            MAX(date) OVER (PARTITION BY trip) AS sort_date
                        FROM expense
                        WHERE category = 'Traveling'
                          AND trip IS NOT NULL
                          AND trip != ''
                        ORDER BY sort_date DESC;
                    """
            cursor.execute(query, ())

            rows = cursor.fetchall()
            return [
                row[0]
                for row in rows
                if row[0] is not None and str(row[0]).strip()
            ]

        except psycopg2.Error as e:
            st.error(f"Error retrieving trip data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []



def fetch_trip_expense(trip):
    """Fetches annual expense data from the database."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
         # To calculate total_spending by trip and the % for category in SQL first
        query = """
                SELECT
                    trip,
                    traveling_category,
                    SUM(amount) AS category_spending,
                    ROUND(SUM(
                        COALESCE(
                            (amount / NULLIF(amount_for_number_of_travelers, 0))
                            * paid_for_number_of_travlerers,
                            0
                        )
                    ), 2) AS category_i_spent,
                    SUM(SUM(amount)) OVER (PARTITION BY trip) AS total_spending,
                    ROUND(SUM(SUM(
                        COALESCE(
                            (amount / NULLIF(amount_for_number_of_travelers, 0))
                            * paid_for_number_of_travlerers,
                            0
                        )
                    )) OVER (PARTITION BY trip), 2) AS total_i_spent,
                    -- Percentage of Total (Safe from Division by Zero)
                    ROUND(
                        (SUM(amount) / NULLIF(SUM(SUM(amount)) OVER (PARTITION BY trip), 0)) * 100.0, 
                    2) AS percentage_total,
                    
                    -- Percentage I Spent (Safe from Division by Zero)
                    ROUND(
                        (
                            SUM(
                                COALESCE(
                                    (amount / NULLIF(amount_for_number_of_travelers, 0))
                                    * paid_for_number_of_travlerers,
                                    0
                                )
                            )
                            / NULLIF(
                                SUM(SUM(
                                    COALESCE(
                                        (amount / NULLIF(amount_for_number_of_travelers, 0))
                                        * paid_for_number_of_travlerers,
                                        0
                                    )
                                )) OVER (PARTITION BY trip),
                                0
                            )
                        ) * 100.0,
                    2) AS percentage_I_spent
                FROM
                    expense
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
            
def fetch_all_trips():
    """Fetches all unique trips from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT DISTINCT trip FROM expense WHERE trip IS NOT NULL AND trip != '';"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [row[0] for row in rows if row[0] is not None and str(row[0]).strip().upper() not in ('NONE', 'NULL', '')]
        except psycopg2.Error as e:
            st.error(f"Error retrieving trips: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []
