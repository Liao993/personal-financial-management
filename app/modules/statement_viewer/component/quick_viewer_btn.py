import streamlit as st # type: ignore
import pandas as pd # type: ignore
from modules.statement_viewer.state_management.state_key import LAST_QUERY_KEY, QUERY_MODE_KEY, UPDATE_PENDING_CONFIRMATION_KEY, PENDING_UPDATE_QUERY_KEY, LAST_STATUS_MESSAGE_KEY, HINT_MODE_KEY, RESULT_DF_KEY
from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query


from modules.statement_viewer.component.viewer_btn.expense_btn import expense_btn
from modules.statement_viewer.component.viewer_btn.transaction_btn import transaction_btn
from modules.statement_viewer.state_management.reset_to_query_state import reset_to_query_mode

def quick_viewer_section():
     # --- 2. Ttitle & Custom Query Button ---
   
    expense_btn()
    transaction_btn()
    query_buttons = st.columns(3)        
    with query_buttons[0]:
        if st.button("💰 View All Income", use_container_width=True):
            execute_predefined_query("SELECT *, SUM(amount) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS year_total FROM income ORDER BY date DESC")
    with query_buttons[1]:
        if st.button("💧 View All Cashflow", use_container_width=True):
            execute_predefined_query("SELECT * FROM cashflow ORDER BY date DESC")
    with query_buttons[2]:
        if st.button("✍️ Write Customized Query", use_container_width=True, key="custom_query_btn",type="primary"):
            reset_to_query_mode() 
         

    
    st.markdown("---")