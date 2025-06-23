import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore


def fetch_statement(inputed_query: str) -> pd.DataFrame:

    conn = get_db_connection() # Explicitly use the reporting user
    if conn:
        cursor = conn.cursor()
        try:
            # --- Added: Check for INSERT or DELETE queries ---
            lower_query = inputed_query.strip().lower()
            if lower_query.startswith("insert") or lower_query.startswith("delete"):
                st.error("Access Denied: You do not have permission to insert or delete items with this user role.")
                return pd.DataFrame() # Reject execution and return empty DataFrame
            # --- End Added Check ---
            
            # Execute the raw SQL query. Removed the empty tuple as it's not for parameterized queries.
            cursor.execute(inputed_query)
            
            # Check if the query returned results (e.g., it was a SELECT query)
            if cursor.description:
                rows = cursor.fetchall()
                cols = [col[0] for col in cursor.description]  # Get column names
                df = pd.DataFrame(rows, columns=cols)
                return df
            else:
                # If no description, it means it was likely a non-SELECT query (UPDATE, INSERT, DDL, etc.)
                # In such cases, there's no data to fetch for a DataFrame.
                st.info("Query executed successfully, but no data to display (e.g., non-SELECT query or DML).")
                return pd.DataFrame()

        except psycopg2.Error as e:
            # Ensure any changes are rolled back if an error occurs
            conn.rollback() 
            st.error(f"Error executing query: {e}. Please check your SQL syntax or permissions.")
            return pd.DataFrame()
        finally:
            # Ensure cursor and connection are closed
            cursor.close()
            conn.close()
    else:
        st.warning("Database connection failed. Cannot execute query.")
        return pd.DataFrame()