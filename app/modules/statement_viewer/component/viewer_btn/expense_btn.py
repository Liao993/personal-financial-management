from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
import streamlit as st # type: ignore
def expense_btn():
    query_buttons = st.columns(6)
    
    with query_buttons[0]:
        if st.button("💸 All Regular Expenses", use_container_width=True):
             execute_predefined_query("""
                                        SELECT 
                                                id, date, items, amount, category,source_notes,
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
                                                category != 'Traveling' and category != 'House'
                                            ORDER BY 
                                                date DESC;
                                     """)
       
    
    with query_buttons[1]:
         if st.button("💸 All House Expenses", use_container_width=True):
            execute_predefined_query("""
                                          SELECT 
                                                id, date, items, amount, category,house_category, house_summary_category,
                                                -- Get yearly Regular Expenses
                                                SUM(CASE WHEN house_summary_category = 'Regular Expenses' THEN amount ELSE 0 END) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS "year_regular_expense",
                                              
                                                -- get yearly total
                                                SUM(CASE WHEN house_category != 'Extra Mortgage' THEN amount ELSE 0 END) OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS "year_total (Excluded Extra Mortgage)"
                                            FROM 
                                                dbt_budget.intermediate_expenses_with_summary
                                            WHERE 
                                                category = 'House'
                                            ORDER BY 
                                                date DESC;
                                     """)
    
    with query_buttons[2]:
         if st.button("💸 All Traveling Expenses", use_container_width=True):
            execute_predefined_query("""
                                     SELECT 
                                            id, date, items, amount, category, trip, traveling_category, 
                                            amount_for_number_of_travelers, paid_for_number_of_travlerers,
                                            -- Calculate the SUM of 'amount' partitioned by the 'trip' column
                                            SUM(amount) OVER (PARTITION BY trip) AS trip_total
                                            FROM 
                                                expense 
                                            WHERE 
                                                category = 'Traveling' 
                                            -- Sorting is now done by the extracted year first, then by the trip name, then by date descending
                                            ORDER BY 
                                                date DESC,
                                                trip,
                                                EXTRACT(YEAR FROM date) desc, 
                                                EXTRACT(MONTH FROM date) desc

                                                
                                                                                
                                     """)
   
    with query_buttons[3]:
        if st.button("💸 Expenses by Category", use_container_width=True):
            execute_predefined_query("""
                                     SELECT category, 
                                        EXTRACT(YEAR FROM date) AS year,
                                        SUM(amount) AS total_amount,
                                        -- Get total spending excluding house
                                        SUM(SUM(CASE WHEN category != 'House' THEN amount ELSE 0 END))
                                             OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS "total_yearly_expense (Excluding House)",
                                        -- Get House spending
                                        SUM(SUM(CASE WHEN category = 'House' and house_category != 'Extra Mortgage' THEN amount ELSE 0 END))
                                             OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS "total_yearly_expense (House)",
                                        -- total spending of the year - exclude extra mortgage
                                        SUM(SUM(CASE WHEN house_category != 'Extra Mortgage' OR house_category IS NULL THEN amount ELSE 0 END))
                                            OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS "total_yearly_expense"
                                     FROM expense 
                                  
                                     GROUP BY category, EXTRACT(YEAR FROM date)
                                    ORDER BY year DESC, total_amount DESC
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
    with query_buttons[5]:
        if st.button("💸 Payment Method Expenses", use_container_width=True):
            execute_predefined_query("""
                                    SELECT  
                                            source_notes as payment_method,
                                            Extract(YEAR FROM date) AS year,                                            
                                            Extract(Month FROM date) AS month,
                                            SUM(amount) AS total_amount_by_payment_method
                                
                                        FROM
                                            expense
                                        WHERE
                                            category != 'Traveling' and date>'2025-10-31'
                                     
                                        Group by  source_notes, Extract(YEAR FROM date), Extract(Month FROM date)
                                        ORDER BY  Extract(YEAR FROM date) DESC, Extract(Month FROM date) DESC
                                                                                                                                 
                                     """)
   

    st.write("")