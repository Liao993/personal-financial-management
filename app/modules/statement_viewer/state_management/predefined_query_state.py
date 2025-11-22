import streamlit as st # type: ignore
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY

def execute_predefined_query(query):
    """
    Sets the session state to execute a predefined SELECT query immediately.
    """
    st.session_state[LAST_QUERY_KEY] = query
    st.session_state[QUERY_MODE_KEY] = False
    st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
    st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
    st.session_state[LAST_STATUS_MESSAGE_KEY] = ""
    st.session_state[HINT_MODE_KEY] = False 
    st.rerun()