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
        st.session_state[LAST_QUERY_KEY] = "SELECT * FROM expense ORDER BY date DESC LIMIT 5;" # Default query
    if RESULT_DF_KEY not in st.session_state:
        st.session_state[RESULT_DF_KEY] = pd.DataFrame()
    if HINT_MODE_KEY not in st.session_state:
        st.session_state[HINT_MODE_KEY] = False

    # --- Query Input Mode ---
    if st.session_state[QUERY_MODE_KEY]:
        st.subheader("Enter your SQL query:")
        query_input = st.text_area(
            "SQL Query",
            value=st.session_state[LAST_QUERY_KEY], # Pre-fill with last query
            height=250,
            help="Enter your custom SQL SELECT query. For security, only SELECT queries are recommended."
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
            st.rerun() # Trigger a rerun to display results
     

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

          

            # CSV Download Button
            csv_data = df_results.to_csv(index=False).encode('utf-8')
    
            st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name="results.csv",
            mime="text/csv",
            help="Download the query results as a CSV file."
            )
            # --- End Download Buttons ---
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
