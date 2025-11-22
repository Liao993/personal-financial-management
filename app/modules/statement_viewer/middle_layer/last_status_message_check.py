from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY
import streamlit as st # type: ignore

def check_last_status_message():
    # Display last status message if any (from previous DML/DDL operation)
    if st.session_state[LAST_STATUS_MESSAGE_KEY]:
        if "Error" in st.session_state[LAST_STATUS_MESSAGE_KEY]:
            st.error(st.session_state[LAST_STATUS_MESSAGE_KEY])
        elif "successful" in st.session_state[LAST_STATUS_MESSAGE_KEY]:
            st.success(st.session_state[LAST_STATUS_MESSAGE_KEY])
        else:
            st.info(st.session_state[LAST_STATUS_MESSAGE_KEY])
        st.session_state[LAST_STATUS_MESSAGE_KEY] = "" # Clear after display