import streamlit as st # type: ignore
import pandas as pd # type: ignore
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY
from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
from modules.statement_viewer.state_management.reset_to_query_state import reset_to_query_mode


def quick_viewer_section():
     # --- 2. Quick Action Buttons ---
    st.subheader("Quick Actions")
    query_buttons = st.columns(5)
    
    with query_buttons[0]:
        if st.button("💸 View All Expenses", use_container_width=True):
            execute_predefined_query("SELECT * FROM expense ORDER BY date DESC")
            
    with query_buttons[1]:
        if st.button("💰 View All Income", use_container_width=True):
            execute_predefined_query("SELECT * FROM income ORDER BY date DESC")
            
    with query_buttons[2]:
        if st.button("📈 View All Transactions", use_container_width=True):
            execute_predefined_query("SELECT * FROM transactions ORDER BY date DESC")

    with query_buttons[3]:
        if st.button("💧 View All Cashflow", use_container_width=True):
            execute_predefined_query("SELECT * FROM cashflow ORDER BY date DESC")
    with query_buttons[4]:
        if st.button("✍️ Write Customized Query", use_container_width=True, key="custom_query_btn"):
            reset_to_query_mode()      

    st.markdown("---")