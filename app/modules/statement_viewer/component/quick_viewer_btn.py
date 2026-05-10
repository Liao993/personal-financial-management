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
    query_buttons = st.columns(4)        
    with query_buttons[0]:
        if st.button("✍️ Write Customized Query", use_container_width=True, key="custom_query_btn",type="primary"):
            reset_to_query_mode() 
    with query_buttons[1]: 
        if st.button("💰 View All Income", use_container_width=True):
            execute_predefined_query("SELECT *, SUM(amount) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS year_total FROM income ORDER BY date DESC")

    with query_buttons[2]:
        if st.button("📈 All Deposit", use_container_width=True):
            execute_predefined_query("""
                                        SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account,
                                            sum(amount) over (partition by fund_category) AS fund_category_total_amount
                                        FROM transactions 
                                        WHERE transaction_type = 'Deposit'
                                        ORDER BY fund_category, date DESC
                                     """)
    
    with query_buttons[3]:
        if st.button("📈 All Transfer", use_container_width=True):
            execute_predefined_query("""
                                        SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account,
                                            sum(amount) over (partition by fund_category) AS fund_category_total_amount
                                        FROM transactions 
                                        WHERE transaction_type Like '%Transfer%'
                                        ORDER BY date DESC, fund_category, transaction_id DESC
                                     """)  
    st.markdown("---")

