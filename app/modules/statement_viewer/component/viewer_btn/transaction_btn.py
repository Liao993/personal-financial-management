from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
import streamlit as st # type: ignore

def transaction_btn():
    query_buttons = st.columns(6)        
            

    with query_buttons[0]:
        if st.button("📈 All Monthly Calculation", use_container_width=True):
            execute_predefined_query("SELECT * FROM transactions where source_notes LIKE 'saved from%' ORDER BY date DESC")   
    
    with query_buttons[1]:
        if st.button("📈 All by Fund Category", use_container_width=True):
            execute_predefined_query("SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account FROM transactions ORDER BY fund_category, date DESC")

    with query_buttons[2]:
        if st.button("📈 All by Account", use_container_width=True):
            execute_predefined_query("SELECT *  FROM transactions ORDER BY account_name, date DESC")

    with query_buttons[3]:
        if st.button("📈 All Deposit", use_container_width=True):
            execute_predefined_query("SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account FROM transactions where transaction_type = 'Deposit' ORDER BY fund_category, date DESC")

    with query_buttons[4]:
        if st.button("📈 All Withdrawal", use_container_width=True):
            execute_predefined_query("SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account FROM transactions where transaction_type = 'Withdrawal' ORDER BY fund_category, date DESC")    
    
    with query_buttons[5]:
        if st.button("📈 All Transfer", use_container_width=True):
            execute_predefined_query("SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account FROM transactions where transaction_type Like '%Transfer%' ORDER BY fund_category, date DESC")    
    
    
    st.write("")
