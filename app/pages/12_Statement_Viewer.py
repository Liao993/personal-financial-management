import streamlit as st # type: ignore
import pandas as pd
import io # Import io for handling byte streams for Excel

from backend.statement_backend import fetch_statement
from modules.statement_viewer.hint import hint_page

# --- Session State Management ---
# Keys for managing the page's state
QUERY_MODE_KEY = 'statement_query_mode' # True: show input, False: show results
LAST_QUERY_KEY = 'statement_last_query' # Stores the query last submitted
RESULT_DF_KEY = 'statement_result_df'   # Stores the DataFrame result
HINT_MODE_KEY = 'statement_hint_mode' # True: show hints, False: hide hints

# Keys for handling DML/DDL confirmation
UPDATE_PENDING_CONFIRMATION_KEY = 'statement_update_pending_confirmation'
PENDING_UPDATE_QUERY_KEY = 'statement_pending_update_query'
LAST_STATUS_MESSAGE_KEY = 'statement_last_status_message' # To store messages for display

st.set_page_config(
    page_title="Statement Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def statement_page():
    st.markdown("<h1 style='color: lightcoral; text-align: center;'>Custom SQL Query Viewer</h1>", unsafe_allow_html=True)

    # Initialize session state variables if they don't exist
    if QUERY_MODE_KEY not in st.session_state:
        st.session_state[QUERY_MODE_KEY] = True # Start in query input mode
    if LAST_QUERY_KEY not in st.session_state:
        st.session_state[LAST_QUERY_KEY] = "SELECT * FROM" # Default query
    if RESULT_DF_KEY not in st.session_state:
        st.session_state[RESULT_DF_KEY] = pd.DataFrame()
    if HINT_MODE_KEY not in st.session_state:
        st.session_state[HINT_MODE_KEY] = False
    
    # Initialize DML/DDL specific session states
    if UPDATE_PENDING_CONFIRMATION_KEY not in st.session_state:
        st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
    if PENDING_UPDATE_QUERY_KEY not in st.session_state:
        st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
    if LAST_STATUS_MESSAGE_KEY not in st.session_state:
        st.session_state[LAST_STATUS_MESSAGE_KEY] = ""

    # Display last status message if any (from previous DML/DDL operation)
    if st.session_state[LAST_STATUS_MESSAGE_KEY]:
        if "Error" in st.session_state[LAST_STATUS_MESSAGE_KEY]:
            st.error(st.session_state[LAST_STATUS_MESSAGE_KEY])
        elif "successful" in st.session_state[LAST_STATUS_MESSAGE_KEY]:
            st.success(st.session_state[LAST_STATUS_MESSAGE_KEY])
        else:
            st.info(st.session_state[LAST_STATUS_MESSAGE_KEY])
        st.session_state[LAST_STATUS_MESSAGE_KEY] = "" # Clear after display


    # --- Query Input Mode ---
    if st.session_state[QUERY_MODE_KEY]:
        st.subheader("Enter your SQL query:")
        query_input = st.text_area(
            "SQL Query",
            value=st.session_state[LAST_QUERY_KEY], # Pre-fill with last query
            height=250,
            help="Enter your custom SQL query. SELECT returns data. INSERT/UPDATE/DELETE/DDL queries require confirmation and return status messages."
        )
        cols = st.columns(2)
        with cols[0]:
          submit_button = st.button("Submit Query")
        with cols[1]:
           # Change button label based on HINT_MODE_KEY
            hint_button_label = "Hide Hints" if st.session_state[HINT_MODE_KEY] else "Show Hints"
            hint_button = st.button(hint_button_label)

         # --- Hint Button Logic ---
        if hint_button:
            # Toggle the hint mode
            st.session_state[HINT_MODE_KEY] = not st.session_state[HINT_MODE_KEY]
            st.rerun() # Rerun to reflect the change in hint visibility and button label
        
         # --- Display Hints if HINT_MODE_KEY is True ---
        if st.session_state[HINT_MODE_KEY]:
            hint_page() # Call the hint page function to display hints

        if submit_button:
            st.session_state[LAST_QUERY_KEY] = query_input # Store the query for later display/rerun
            st.session_state[QUERY_MODE_KEY] = False      # Switch to results mode
            # Reset confirmation flags when a new query is submitted
            st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
            st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
            st.session_state[LAST_STATUS_MESSAGE_KEY] = "" # Clear old messages
            st.rerun() # Trigger a rerun to display results
     
        st.info("💡 Tip: Try `SELECT * FROM income LIMIT 5;` or `INSERT INTO income (amount, date, category) VALUES (150, '2025-01-01', 'Salary');`")
        st.warning("""
            ⚠️ **Security Alert:** Allowing arbitrary SQL queries directly from user input is a **significant security risk**.
            Use with caution. For production, strictly validate inputs or provide predefined queries.
        """)

    # --- Results Display / Confirmation Mode ---
    else:
        # --- Handle DML/DDL query confirmation ---
        if st.session_state[UPDATE_PENDING_CONFIRMATION_KEY]:
            st.warning("A DML/DDL query was detected. Please review and confirm to execute.")
            st.code(st.session_state[PENDING_UPDATE_QUERY_KEY], language='sql')

            col1, col2 = st.columns(2)
            with col1:
                confirm_dml_button = st.button("Confirm and Execute Query")
            with col2:
                cancel_dml_button = st.button("Cancel Query")

            if confirm_dml_button:
                st.info("Executing confirmed DML/DDL query...")
                # Call backend with confirm_action=True to execute
                df_results_after_dml, status_msg = fetch_statement(
                    st.session_state[PENDING_UPDATE_QUERY_KEY],
                    confirm_action=True # Tell backend to execute
                )
                
                st.session_state[LAST_STATUS_MESSAGE_KEY] = status_msg # Store message
                
                # Reset flags and return to query input mode
                st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
                st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
                st.session_state[QUERY_MODE_KEY] = True # Go back to input
                st.rerun() # Rerun to display the status message

            elif cancel_dml_button:
                st.session_state[LAST_STATUS_MESSAGE_KEY] = "DML/DDL query cancelled."
                # Reset flags and return to query input mode
                st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
                st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
                st.session_state[QUERY_MODE_KEY] = True # Go back to input
                st.rerun()
        
        # --- Display results for SELECT or handle other non-DataFrame queries ---
        else:
            st.info("Working on your query...")
            # Fetch data using the backend function. Initial call for non-DML/DDL or to detect DML/DDL.
            df_results, status_msg = fetch_statement(st.session_state[LAST_QUERY_KEY], confirm_action=False)

            # Check if fetch_statement detected DML/DDL and set the pending flag
            if st.session_state[UPDATE_PENDING_CONFIRMATION_KEY]:
                # If a DML/DDL is now pending, rerunn to display the confirmation UI
                st.rerun()
            elif not df_results.empty:
                st.subheader("Query Results:")
                st.dataframe(df_results, use_container_width=True)
                st.session_state[RESULT_DF_KEY] = df_results

                # --- Download Buttons ---
                st.write("---") # Separator for download buttons
                download_cols = st.columns(2)
                
                # CSV Download Button
                csv_data = df_results.to_csv(index=False).encode('utf-8')
                with download_cols[0]:
                    st.download_button(
                        label="Download as CSV",
                        data=csv_data,
                        file_name="query_results.csv",
                        mime="text/csv",
                        help="Download the query results as a CSV file."
                    )

              
                # --- End Download Buttons ---
            elif status_msg: # If df_results is empty but there's a status message (e.g., SELECT no rows, or backend error)
                if "Error" in status_msg:
                    st.error(status_msg)
                else:
                    st.info(status_msg)
            else:
                st.warning("No data returned for SELECT query and no specific status message.")


        # Button to return to query input
        refresh_button = st.button("Enter New Query / Refresh")
        if refresh_button:
            st.session_state[QUERY_MODE_KEY] = True # Go back to query input
            st.session_state[RESULT_DF_KEY] = pd.DataFrame() # Clear previous results
            st.session_state[HINT_MODE_KEY] = False # Ensure hints are hidden
            # Ensure DML/DDL specific flags are also reset
            st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
            st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
            st.session_state[LAST_STATUS_MESSAGE_KEY] = "" # Clear old messages
            st.rerun() # Trigger a rerun

# This block allows you to run the page directly for testing
if __name__ == "__main__":
    statement_page()
