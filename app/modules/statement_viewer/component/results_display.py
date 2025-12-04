import streamlit as st # type: ignore
import pandas as pd
import io 

from modules.statement_viewer.state_management.reset_to_query_state import reset_to_query_mode
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY

# Assuming fetch_statement is available through the app's structure
from backend.statement_backend import fetch_statement 
def results_display_section():
    """
    Handles DML/DDL confirmation flow OR executes SELECT query and displays results.
    """
    
    # --- Handle DML/DDL query confirmation ---
    if st.session_state[UPDATE_PENDING_CONFIRMATION_KEY]:
        st.warning("A DML/DDL query was detected. Please review and confirm to execute.")
        #print out the query
        st.code(st.session_state[PENDING_UPDATE_QUERY_KEY], language='sql')

        col1, col2 = st.columns(2)
        with col1:
            confirm_dml_button = st.button("Confirm and Execute Query", use_container_width=True)
        with col2:
            cancel_dml_button = st.button("Cancel Query", use_container_width=True)

        if confirm_dml_button:
            st.info("Executing confirmed DML/DDL query...")
            # Call backend with confirm_action=True to execute
            df_results_after_dml, status_msg = fetch_statement(
                st.session_state[PENDING_UPDATE_QUERY_KEY],
                confirm_action=True # Tell backend to execute
            )
            
            st.session_state[LAST_STATUS_MESSAGE_KEY] = status_msg # Store message
            if "successful" in st.session_state[LAST_STATUS_MESSAGE_KEY]:
                st.success(st.session_state[LAST_STATUS_MESSAGE_KEY])          
                
            else:
                st.error(st.session_state[LAST_STATUS_MESSAGE_KEY])
            

        elif cancel_dml_button:
            st.session_state[LAST_STATUS_MESSAGE_KEY] = "DML/DDL query cancelled."
            reset_to_query_mode()
          
    
    # --- Execute and Display SELECT results ---
    else:
        
        # Fetch data. Initial call for non-DML/DDL or to detect DML/DDL.
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
            st.write("---") 
            download_cols = st.columns(2)
            
            # CSV Download Button
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            with download_cols[0]:
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name="query_results.csv",
                    mime="text/csv",
                    help="Download the query results as a CSV file.",
                    use_container_width=True
                )
            with download_cols[1]:
                pass 

        elif status_msg: # If df_results is empty but there's a status message (e.g., SELECT no rows, or backend error)
            if "Error" in status_msg:
                st.error(status_msg)
            else:
                st.info(status_msg)
        else:
            st.warning("No data returned for SELECT query and no specific status message.")