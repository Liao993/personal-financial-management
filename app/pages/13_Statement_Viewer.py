import streamlit as st # type: ignore
import pandas as pd
import io 

# Import the components
from modules.statement_viewer.component.query_input_box import query_input_section
from modules.statement_viewer.component.results_display import results_display_section
from modules.statement_viewer.component.quick_viewer_btn import quick_viewer_section

from modules.statement_viewer.middle_layer.last_status_message_check import check_last_status_message
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY

from modules.statement_viewer.state_management.reset_to_query_state import reset_to_query_mode
from modules.statement_viewer.state_management.init_session_state import init_session_state
# Global setup block (only runs once)
st.set_page_config(
    page_title="Statement Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def statement_page():
    # --- 1. Initialization State Management ---
    init_session_state()
    
  
    st.markdown("<h1 style='color: orange; text-align: center;'>Custom SQL Query Viewer</h1>", unsafe_allow_html=True)

    # Display last status message if any (from previous DML/DDL operation)
    check_last_status_message()

    # --- 2. Quick Viewer Button ---
    quick_viewer_section()

    # --- 3. Main Application Flow Control ---
    if st.session_state[QUERY_MODE_KEY]:
        # Renders the text area, Submit, and Hint button/content
        query_input_section()
     
    else:
        # Renders the results table, DML confirmation, and status messages
        results_display_section()
        
        # Button to return to query input (only shown after results/confirmation)
        st.write("---")

        refresh_button = st.button("Back to Query Input")
        if refresh_button:
            reset_to_query_mode()


# This block allows you to run the page directly for testing
if __name__ == "__main__":
    statement_page()