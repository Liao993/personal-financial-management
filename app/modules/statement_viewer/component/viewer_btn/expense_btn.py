from modules.statement_viewer.state_management.predefined_query_state import execute_predefined_query
import streamlit as st  # type: ignore


def expense_btn():
    query_buttons = st.columns(6)

    with query_buttons[0]:
        if st.button("💸 All Regular Expenses", use_container_width=True):
            execute_predefined_query("""
                SELECT
                    id, date, items, amount, category, payment_method, source_notes,
                    -- get grocery total
                    SUM(CASE WHEN category = 'Grocery' THEN amount ELSE 0 END)
                        OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS grocery_year_total,
                    -- get donation total
                    SUM(CASE WHEN category = 'Donation' THEN amount ELSE 0 END)
                        OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS donation_year_total,
                    -- get yearly total
                    SUM(amount)
                        OVER (PARTITION BY EXTRACT(YEAR FROM date)) AS year_total
                FROM expense
                WHERE category != 'Traveling'
                  AND category != 'House'
                  AND house_category IS NULL
                  AND exclude_from_monthly = FALSE
                ORDER BY payment_method NULLS LAST, date DESC, id DESC;
            """)

    with query_buttons[1]:
        if st.button("💸 All House Expenses", use_container_width=True):
            execute_predefined_query("""
                SELECT
                    id, date, items, amount, category, payment_method, house_category,
                    exclude_from_monthly,
                    CASE
                        WHEN house_category = 'Mortgage' THEN 'Mortgage'
                        WHEN house_category = 'Extra Mortgage' THEN 'Extra Mortgage'
                        WHEN house_category IN (
                            'Internet', 'Electricity', 'Insurance',
                            'Water & Sewage', 'Oil', 'Snow Removal'
                        ) THEN 'Regular Expenses'
                        WHEN house_category LIKE '%Repair%' THEN 'Repairs'
                        WHEN house_category LIKE '%Tax%' THEN 'Tax'
                        ELSE 'Other'
                    END AS house_summary_category,
                    SUM(CASE
                            WHEN house_category IN (
                                'Internet', 'Electricity', 'Insurance',
                                'Water & Sewage', 'Oil', 'Snow Removal'
                            )
                            THEN amount ELSE 0
                        END)
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS "year_regular_expense",
                    SUM(CASE WHEN house_category != 'Extra Mortgage'
                             THEN amount ELSE 0 END)
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS "year_total (Excluded Extra Mortgage)"
                FROM expense
                WHERE category = 'House'
                   OR house_category IS NOT NULL
                ORDER BY payment_method NULLS LAST, date DESC, id DESC;
            """)

    with query_buttons[2]:
        if st.button("💸 All Traveling Expenses", use_container_width=True):
            execute_predefined_query("""
                SELECT
                    id, date, items, amount, category, payment_method, trip,
                    traveling_category,
                    exclude_from_monthly,
                    amount_for_number_of_travelers,
                    paid_for_number_of_travlerers,
                    SUM(amount) OVER (PARTITION BY trip) AS trip_total
                FROM expense
                WHERE category = 'Traveling'
                ORDER BY payment_method NULLS LAST, date DESC, trip,
                         EXTRACT(YEAR  FROM date) DESC,
                         EXTRACT(MONTH FROM date) DESC;
            """)

    with query_buttons[3]:
        if st.button("💸 Expenses by Category", use_container_width=True):
            execute_predefined_query("""
                WITH no_prepaid AS (
                    SELECT *
                    FROM expense
                    WHERE (house_category != 'Extra Mortgage' OR house_category IS NULL)
                )
                SELECT
                    EXTRACT(YEAR FROM date)                                             AS year,
                    category,
                    exclude_from_monthly,
                    SUM(amount)                                                         AS total_amount,
                    SUM(SUM(CASE WHEN category != 'House' THEN amount ELSE 0 END))
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS total_yearly_expense_excluding_house,
                    SUM(SUM(CASE WHEN category = 'House' THEN amount ELSE 0 END))
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS total_yearly_expense_including_house,
                    SUM(SUM(amount))
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS total_yearly_expense
                FROM no_prepaid
                GROUP BY category, exclude_from_monthly, EXTRACT(YEAR FROM date)
                ORDER BY year DESC, exclude_from_monthly, total_amount DESC;
            """)

    with query_buttons[4]:
        if st.button("💸 Grocery Store Expenses", use_container_width=True):
            execute_predefined_query("""
                SELECT
                    EXTRACT(YEAR FROM date) AS year,
                    CASE
                        WHEN UPPER(items) LIKE '%SUPER%'             THEN 'Loblaws'
                        WHEN UPPER(items) LIKE '%NOFRILL%'           THEN 'Loblaws'
                        WHEN UPPER(items) LIKE '%MIKE & ANDREEA''S%' THEN 'Loblaws'
                        WHEN UPPER(items) LIKE '%COSTCO%'            THEN 'Costco'
                        WHEN UPPER(items) LIKE '%SOBEY%'             THEN 'Sobeys'
                        ELSE 'OTHERS'
                    END AS grocery_store,
                    SUM(amount) AS total_amount_by_store,
                    SUM(SUM(CASE WHEN category = 'Grocery' THEN amount ELSE 0 END))
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS total_yearly_grocery_expense,
                    SUM(SUM(amount))
                        OVER (PARTITION BY EXTRACT(YEAR FROM date))
                        AS total_yearly_expense
                FROM expense
                WHERE category != 'Traveling'
                  AND house_category IS NULL
                  AND exclude_from_monthly = FALSE
                  AND (
                        UPPER(items) LIKE '%SUPER%'
                     OR UPPER(items) LIKE '%SOBEY%'
                     OR UPPER(items) LIKE '%NOFRILL%'
                     OR UPPER(items) LIKE '%MIKE & ANDREEA''S%'
                     OR category = 'Grocery'
                  )
                GROUP BY EXTRACT(YEAR FROM date), grocery_store
                ORDER BY EXTRACT(YEAR FROM date) DESC, total_amount_by_store DESC;
            """)

    with query_buttons[5]:
        if st.button("💸 Payment Method Expenses", use_container_width=True):
            execute_predefined_query("""
                SELECT
                    payment_method,
                    EXTRACT(YEAR  FROM date) AS year,
                    EXTRACT(MONTH FROM date) AS month,
                    exclude_from_monthly,
                    SUM(amount)              AS total_amount_by_payment_method
                FROM expense
                WHERE category != 'Traveling'
                  AND date > '2025-10-31'
                  AND payment_method IS NOT NULL
                GROUP BY payment_method,
                         exclude_from_monthly,
                         EXTRACT(YEAR  FROM date),
                         EXTRACT(MONTH FROM date)
                ORDER BY payment_method,
                         EXTRACT(YEAR  FROM date) DESC,
                         EXTRACT(MONTH FROM date) DESC;
            """)

    st.write("")
