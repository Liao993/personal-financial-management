from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY
import streamlit as st # type: ignore
import pandas as pd

def init_session_state():
    """Initializes all necessary session state variables."""
    if QUERY_MODE_KEY not in st.session_state:
        st.session_state[QUERY_MODE_KEY] = True 
    if LAST_QUERY_KEY not in st.session_state:
        st.session_state[LAST_QUERY_KEY] = "SELECT * FROM expense LIMIT 10" 
    if RESULT_DF_KEY not in st.session_state:
        st.session_state[RESULT_DF_KEY] = pd.DataFrame()
    if HINT_MODE_KEY not in st.session_state:
        st.session_state[HINT_MODE_KEY] = False
    if UPDATE_PENDING_CONFIRMATION_KEY not in st.session_state:
        st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
    if PENDING_UPDATE_QUERY_KEY not in st.session_state:
        st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
    if LAST_STATUS_MESSAGE_KEY not in st.session_state:
        st.session_state[LAST_STATUS_MESSAGE_KEY] = ""