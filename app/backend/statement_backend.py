import streamlit as st
from utils.connection import get_db_connection # Assumed to return a connection for a privileged user
import psycopg2
import pandas as pd
from typing import Tuple

# Define session state keys (these should match the frontend's keys)
# These keys are used to communicate pending DML/DDL actions to the Streamlit frontend.
UPDATE_PENDING_CONFIRMATION_KEY = 'statement_update_pending_confirmation'
PENDING_UPDATE_QUERY_KEY = 'statement_pending_update_query'


def fetch_statement(inputed_query: str, confirm_action: bool = False) -> Tuple[pd.DataFrame, str]:
    """
    Executes a SQL query provided by the user. For SELECT queries, it fetches data
    into a Pandas DataFrame. For INSERT, UPDATE, DELETE, and DDL queries, it
    returns a status message indicating success, error, or pending confirmation.

    Args:
        inputed_query (str): The SQL query string to execute.
        confirm_action (bool): If True, DML/DDL queries are executed immediately.
                               If False, DML/DDL queries trigger a pending confirmation state
                               in the Streamlit session.

    Returns:
        Tuple[pd.DataFrame, str]:
            - pd.DataFrame: Results for SELECT queries; an empty DataFrame otherwise.
            - str: A status message (e.g., success, error, or instruction for pending DML/DDL).
    """
    # Get a database connection. Assuming this connection has necessary DML/DDL permissions.
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame(), "Database connection failed. Cannot execute query."

    cursor = conn.cursor()
    try:
        lower_query = inputed_query.strip().lower()
        query_type = ""

        # Determine the type of query based on its starting keyword
        if lower_query.startswith("select"):
            query_type = "SELECT"
        elif lower_query.startswith("update"):
            query_type = "UPDATE"
        elif lower_query.startswith("insert"):
            query_type = "INSERT"
        elif lower_query.startswith("delete"):
            query_type = "DELETE"
        # Check for Data Definition Language (DDL) queries
        elif any(lower_query.startswith(keyword) for keyword in ["create", "drop", "alter", "truncate"]):
            query_type = "DDL"
        else:
            # Handle unsupported query types
            return pd.DataFrame(), "Unsupported query type. Only SELECT, INSERT, UPDATE, DELETE, and basic DDL are supported."

        # --- Handle DML (INSERT, UPDATE, DELETE) and DDL Queries ---
        if query_type in ["INSERT", "UPDATE", "DELETE", "DDL"]:
            if not confirm_action:
                # If a DML/DDL query is detected but 'confirm_action' is False,
                # it means the frontend needs to ask for user confirmation.
                # We store the query in session state and set a flag.
                st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = True
                st.session_state[PENDING_UPDATE_QUERY_KEY] = inputed_query
                return pd.DataFrame(), "DML/DDL query detected. Please confirm to execute."
            else:
                # If 'confirm_action' is True, the user has confirmed, so execute the query.
                cursor.execute(inputed_query)
                conn.commit() # Commit the transaction for DML/DDL operations

                # Get the number of rows affected for INSERT, UPDATE, DELETE.
                # DDL operations usually don't affect rows in the same way.
                affected_rows = cursor.rowcount if query_type in ["INSERT", "UPDATE", "DELETE"] else 0
                
                # Return a success message with details
                return pd.DataFrame(), f"Operation successful ({query_type}): {affected_rows} rows affected."

        # --- Handle SELECT Queries ---
        elif query_type == "SELECT":
            cursor.execute(inputed_query)
            if cursor.description:
                # If there's a description, it means data was returned (like a SELECT statement).
                rows = cursor.fetchall()
                cols = [col[0] for col in cursor.description] # Extract column names
                df = pd.DataFrame(rows, columns=cols)
                return df, "" # Return the DataFrame and an empty status string
            else:
                # A SELECT query might execute but return no rows.
                return pd.DataFrame(), "SELECT query executed, but no data was returned."

    except psycopg2.Error as e:
        # If any database error occurs, rollback the transaction to maintain data integrity.
        conn.rollback()
        return pd.DataFrame(), f"Error executing query: {e}. Please check your SQL syntax or database permissions."
    finally:
        # Ensure the cursor and connection are always closed, regardless of success or failure.
        if cursor:
            cursor.close()
        if conn:
            conn.close()
