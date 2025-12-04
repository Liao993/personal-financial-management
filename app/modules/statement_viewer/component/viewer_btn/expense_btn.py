from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
import streamlit as st # type: ignore
def expense_btn():
    query_buttons = st.columns(5)
    
    with query_buttons[0]:
        if st.button("💸 All Expenses", use_container_width=True):
            execute_predefined_query("""
                                          SELECT 
                                                *,
                                                -- get donation total
                                                SUM(CASE 
                                                        WHEN category = 'Donation' THEN amount 
                                                        ELSE 0 
                                                    END) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS donation_year_total,
                                                -- get yearly total
                                                SUM(amount) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS year_total
                                            FROM 
                                                expense 
                                            ORDER BY 
                                                date DESC;
                                     """)
    
    with query_buttons[1]:
        if st.button("💸 All Non-Traveling Expenses", use_container_width=True):
             execute_predefined_query("""
                                        SELECT 
                                                id, date, items, amount, category,
                                                -- get grocery total
                                                SUM(CASE
                                                        WHEN category = 'Grocery' THEN amount
                                                        ELSE 0
                                                    END) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS grocery_year_total,
                                                -- get donation total
                                                SUM(CASE 
                                                        WHEN category = 'Donation' THEN amount 
                                                        ELSE 0 
                                                    END) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS donation_year_total,
                                                -- get yearly total
                                                SUM(amount) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS year_total
                                            FROM 
                                                expense 
                                            WHERE 
                                                category != 'Traveling' 
                                            ORDER BY 
                                                date DESC;
                                     """)
    
    with query_buttons[2]:
        if st.button("💸 Expenses by Category", use_container_width=True):
            execute_predefined_query("SELECT category, SUM(amount) AS total_amount FROM expense GROUP BY category ORDER BY total_amount DESC")
   
    with query_buttons[3]:
        if st.button("💸 All Traveling Expenses", use_container_width=True):
            execute_predefined_query("""
                                     SELECT 
                                            *, 
                                            -- Calculate the SUM of 'amount' partitioned by the 'trip' column
                                            SUM(amount) OVER (PARTITION BY trip) AS trip_total
                                            FROM 
                                                expense 
                                            WHERE 
                                                category = 'Traveling' 
                                            -- Sorting is now done by the extracted year first, then by the trip name, then by date descending
                                            ORDER BY 
                                                EXTRACT(YEAR FROM date) desc, 
                                                EXTRACT(MONTH FROM date) desc,
                                                trip, 
                                                date DESC;
                                                                                
                                     """)
    with query_buttons[4]:
        if st.button("💸 Grocery Store Expenses", use_container_width=True):
            execute_predefined_query("""
                                    SELECT  Extract(YEAR FROM date) AS year,                                            
                                            CASE 
                                                WHEN  UPPER(items) LIKE '%SUPER%' THEN 'Loblaws'
                                                WHEN  UPPER(items) LIKE '%NOFRILL%' THEN 'Loblaws'
                                                WHEN  UPPER(items) LIKE '%MIKE & ANDREEA''S%' THEN 'Loblaws'
                                                WHEN  UPPER(items) LIKE '%COSTCO%' THEN 'Costco'
                                                WHEN  UPPER(items) LIKE '%SOBEY%' THEN 'Sobeys'
                                                ELSE 'OTHERS'
                                            END AS grocery_store,
                                            SUM(amount) AS total_amount_by_store,
                                     -- Get yearly grocery total
                                            SUM(
                                                SUM(CASE WHEN category = 'Grocery' THEN amount ELSE 0 END) 
                                                ) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS total_yearly_grocery_expense,
                                     -- Get yearly total
                                            SUM(SUM(amount)) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS total_yearly_expense
                                
                                        FROM
                                            expense
                                        WHERE
                                            category != 'Traveling' AND
                                     (
                                            UPPER(items) LIKE '%SUPER%'
                                            OR UPPER(items) LIKE '%SOBEY%'  
                                            OR UPPER(items) LIKE '%NOFRILL%'
                                            OR UPPER(items) LIKE '%MIKE & ANDREEA''S%' 
                                            OR category = 'Grocery'
                                     )
                                        Group by  Extract(YEAR FROM date), grocery_store
                                        ORDER BY  Extract(YEAR FROM date) DESC, total_amount_by_store DESC
                                                                                                                                 
                                     """)
   

    st.write("")