from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
import streamlit as st # type: ignore

def transaction_btn():
    query_buttons = st.columns(6)        
            

    with query_buttons[0]:
        #add window function to get total saving per month
        if st.button("📈 All Monthly Calculation", use_container_width=True):
            execute_predefined_query("""SELECT 
                                            *, -- Selects all original columns from the transactions table
                                            SUM(amount) OVER (
                                                -- TO_CHAR(date, 'YYYY-MM') groups the data by the Year and Month
                                                PARTITION BY TO_CHAR(date, 'YYYY-MM')
                                            ) AS total_saving_for_month
                                        FROM 
                                            transactions 
                                        WHERE 
                                            source_notes LIKE 'saved from%' 
                                        ORDER BY date DESC
                                     """)   
        # add window function to get total amount by fund category
    with query_buttons[1]:
        if st.button("📈 All by Fund Category", use_container_width=True):
            execute_predefined_query("""
                                        SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account,
                                        sum(amount) over (partition by fund_category) AS fund_category_total_amount

                                        FROM transactions 
                                        ORDER BY fund_category, date DESC
                                     """)
        # add window function to get total amount by account
    with query_buttons[2]:
        if st.button("📈 All by Account", use_container_width=True):
            execute_predefined_query("""
                                        SELECT *,
                                            sum(amount) over (partition by account_name) AS account_name_total_amount  
                                        FROM transactions 
                                        ORDER BY account_name, date DESC
                                     """)

        # add window function to get total amount by fund category
    with query_buttons[3]:
        if st.button("📈 All Withdrawal", use_container_width=True):
            execute_predefined_query("""
                                        SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account, prepaid,
                                            sum(amount) over (partition by fund_category) AS fund_category_total_amount
                                        FROM transactions 
                                        WHERE transaction_type = 'Withdrawal'
                                        ORDER BY 
                                        CASE fund_category
                                         WHEN 'Emergency Funds' THEN 1
                                         WHEN 'Retirement Saving' THEN 2
                                         WHEN 'Parents Support' THEN 3
                                         WHEN 'Medium-term Saving' THEN 4
                                         WHEN 'Traveling Funds' THEN 5
                                        END
                                         , date DESC
                                     """) 
    with query_buttons[4]:
        if st.button("📈 All Traveling Withdrawal", use_container_width=True):
            execute_predefined_query("""
                                        SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account, prepaid                                      FROM transactions 
                                        WHERE transaction_type = 'Withdrawal' and fund_category = 'Traveling Funds'
                                        ORDER BY date DESC
                                     """) 
    with query_buttons[5]:
        if st.button("📈 All Medium Withdrawal", use_container_width=True):
            execute_predefined_query("""
                                        SELECT transaction_id, date, fund_category, amount, transaction_type, account_name, source_notes, transfer_to_account, prepaid                                      FROM transactions 
                                        WHERE transaction_type = 'Withdrawal' and fund_category = 'Medium-term Saving'
                                        ORDER BY date DESC
                                     """) 
    
    st.write("")
