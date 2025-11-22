import streamlit as st # type: ignore
from modules.statement_viewer.component.table_hint import table_hint
from modules.statement_viewer.component.syntax_hint import syntax_hint
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY

# --- Session State Keys (re-declared for module scope) ---
QUERY_MODE_KEY = 'statement_query_mode'
LAST_QUERY_KEY = 'statement_last_query'
HINT_MODE_KEY = 'statement_hint_mode'
UPDATE_PENDING_CONFIRMATION_KEY = 'statement_update_pending_confirmation'
PENDING_UPDATE_QUERY_KEY = 'statement_pending_update_query'
LAST_STATUS_MESSAGE_KEY = 'statement_last_status_message'

def query_input_section():
    """
    Displays the query input text area and the Submit/Hint buttons.
    Updates session state upon submission.
    """
    st.subheader("Enter your SQL query:")
    st.warning("""
            ⚠️ **Security Alert:** Allowing arbitrary SQL (Insert/Update/Delete) queries directly from user input is a **significant security risk**.
            Use with caution.
        """)
    
    # 1. Query Text Area
    query_input = st.text_area(
        value=st.session_state[LAST_QUERY_KEY], # Pre-fill with last query
        height=250,
        label="",
    )
    
    # 2. Action Buttons (Submit and Hint)
    cols = st.columns(2)
    with cols[0]:
        submit_button = st.button("Submit Query", use_container_width=True)
    with cols[1]:
        # Change button label based on HINT_MODE_KEY
        hint_button_label = "Hide Hints" if st.session_state[HINT_MODE_KEY] else "Show Hints"
        hint_button = st.button(hint_button_label, use_container_width=True)

    # --- Hint Button Logic ---
    if hint_button:
        # Toggle the hint mode
        st.session_state[HINT_MODE_KEY] = not st.session_state[HINT_MODE_KEY]
        st.rerun() # Rerun to reflect the change in hint visibility and button label
    
    # --- Display Hints if HINT_MODE_KEY is True ---
    if st.session_state[HINT_MODE_KEY]:
        table_hint()
        syntax_hint()

    # --- Submit Button Logic ---
    if submit_button:
        st.session_state[LAST_QUERY_KEY] = query_input # Store the query
        st.session_state[QUERY_MODE_KEY] = False      # Switch to results mode
        # Reset confirmation flags when a new query is submitted
        st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
        st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
        st.session_state[LAST_STATUS_MESSAGE_KEY] = "" # Clear old messages
        st.rerun() # Trigger a rerun to display results