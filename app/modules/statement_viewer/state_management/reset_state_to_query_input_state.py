import streamlit as st # type: ignore
import pandas as pd # type: ignore
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY
def reset_state_to_query_input():
    """Resets all flags to return to the query input section."""
    st.session_state[QUERY_MODE_KEY] = True
    st.session_state[RESULT_DF_KEY] = pd.DataFrame()
    st.session_state[UPDATE_PENDING_CONFIRMATION_KEY] = False
    st.session_state[PENDING_UPDATE_QUERY_KEY] = ""
    st.session_state[LAST_STATUS_MESSAGE_KEY] = ""