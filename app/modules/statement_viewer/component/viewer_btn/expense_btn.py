from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
import streamlit as st # type: ignore
def expense_btn():
    query_buttons = st.columns(6)
    
    with query_buttons[0]:
        if st.button("💸 All Expenses", use_container_width=True):
            execute_predefined_query("SELECT * FROM expense ORDER BY date DESC")
    
    with query_buttons[1]:
        if st.button("💸 All Non-Traveling Expenses", use_container_width=True):
            execute_predefined_query("SELECT * FROM expense where category != 'Traveling' ORDER BY date DESC")
    
    with query_buttons[2]:
        if st.button("💸 Expenses by Category", use_container_width=True):
            execute_predefined_query("SELECT category, SUM(amount) AS total_amount FROM expense GROUP BY category ORDER BY total_amount DESC")
    with query_buttons[3]:
        if st.button("💸 Expenses by Year", use_container_width=True):
            execute_predefined_query("SELECT Extract(YEAR FROM date) AS year, SUM(amount) AS total_amount FROM expense GROUP BY Extract(YEAR FROM date) ORDER BY year")
    with query_buttons[4]:
        if st.button("💸 All Traveling Expenses", use_container_width=True):
            execute_predefined_query("SELECT * FROM expense where category = 'Traveling' ORDER BY date DESC")
    with query_buttons[5]:
        if st.button("💸 Traveling Expenses by Trip", use_container_width=True):
            execute_predefined_query("SELECT trip, SUM(amount) AS total_amount FROM expense where category = 'Traveling' GROUP BY trip ORDER BY total_amount DESC")

    st.write("")