import streamlit as st # type: ignore
import pandas as pd

from backend.statement_backend import fetch_statement

# --- Session State Management ---
# Keys for managing the page's state
QUERY_MODE_KEY = 'statement_query_mode' # True: show input, False: show results
LAST_QUERY_KEY = 'statement_last_query' # Stores the query last submitted
RESULT_DF_KEY = 'statement_result_df'   # Stores the DataFrame result

def statement_page():
    st.markdown("<h1 style='color: lightcoral; text-align: center;'>Custom SQL Query Viewer</h1>", unsafe_allow_html=True)

    # Initialize session state variables if they don't exist
    if QUERY_MODE_KEY not in st.session_state:
        st.session_state[QUERY_MODE_KEY] = True # Start in query input mode
    if LAST_QUERY_KEY not in st.session_state:
        st.session_state[LAST_QUERY_KEY] = "SELECT * FROM expenses ORDER BY date DESC LIMIT 5;" # Default query
    if RESULT_DF_KEY not in st.session_state:
        st.session_state[RESULT_DF_KEY] = pd.DataFrame()

    # --- Query Input Mode ---
    if st.session_state[QUERY_MODE_KEY]:
        st.subheader("Enter your SQL query:")
        query_input = st.text_area(
            "SQL Query",
            value=st.session_state[LAST_QUERY_KEY], # Pre-fill with last query
            height=250,
            help="Enter your custom SQL SELECT query. For security, only SELECT queries are recommended."
        )

        submit_button = st.button("Submit Query")

        if submit_button:
            st.session_state[LAST_QUERY_KEY] = query_input # Store the query for later display/rerun
            st.session_state[QUERY_MODE_KEY] = False      # Switch to results mode
            st.rerun() # Trigger a rerun to display results

        st.info("💡 Tip: Use `SELECT * FROM income LIMIT 5;` or `SELECT * FROM expense WHERE amount > 100;`")
        st.warning("""
            ⚠️ **Security Alert:** Allowing arbitrary SQL queries (especially non-SELECT) directly
            from user input is a **significant security risk** (SQL Injection, data loss).
            For production, strictly validate inputs or provide predefined queries.
        """)

    # --- Results Display Mode ---
    else:
        st.info("Loading your data...")
        # Fetch data using the backend function
        df_results = fetch_statement(st.session_state[LAST_QUERY_KEY])

        if not df_results.empty:
            st.subheader("Query Results:")
            st.dataframe(df_results, use_container_width=True)
            # Store the results so they persist across reruns if needed,
            # though fetch_statement will re-run on each visit to this block.
            st.session_state[RESULT_DF_KEY] = df_results
        else:
            st.warning("No data returned or an error occurred during query execution. Check your query and database logs.")

        # Button to return to query input
        refresh_button = st.button("Enter New Query / Refresh")
        if refresh_button:
            st.session_state[QUERY_MODE_KEY] = True # Go back to query input
            st.session_state[RESULT_DF_KEY] = pd.DataFrame() # Clear previous results
            st.rerun() # Trigger a rerun

# This block allows you to run the page directly for testing
if __name__ == "__main__":
    statement_page()
