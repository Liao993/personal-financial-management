import streamlit as st # type: ignore


def syntax_hint():

    
    # --- SELECT Section ---
    with st.expander("🔍 SELECT (Read Data)"):
        st.markdown("**Basic Selection:**")
        st.code("SELECT * FROM expense LIMIT 10;", language="sql")
        
        st.markdown("**Select Specific Columns:**")
        st.code("SELECT date, amount, source FROM income;", language="sql")

    # --- UPDATE Section ---
    with st.expander("✏️ UPDATE (Edit Data)"):
        st.markdown("**Update a single column based on a condition:**")
        st.code("UPDATE expense SET category = 'Food Outside' WHERE items = 'MCDONALDS';", language="sql")
        
        st.markdown("**Update multiple columns:**")
        st.code("UPDATE income SET amount = 2000, notes = 'Updated Bonus' WHERE id = 5;", language="sql")
        
        st.error("⚠️ **Warning:** Always use a `WHERE` clause! Omitting it will update **every row** in the table.")

    # --- DELETE Section ---
    with st.expander("🗑️ DELETE (Remove Data)"):
        st.markdown("**Delete specific rows:**")
        st.code("DELETE FROM expense WHERE id = 10;", language="sql")
        
        st.markdown("**Delete rows based on category:**")
        st.code("DELETE FROM transactions WHERE fund_category = 'House';", language="sql")
        
        st.error("⚠️ **Warning:** Always use a `WHERE` clause! Omitting it will delete **all data** in the table.")

    # --- INSERT Section ---
    with st.expander("➕ INSERT (Add Data)"):
        st.markdown("**Insert a new row:**")
        st.code("""
                INSERT INTO expense (date, items, amount, category, traveling_category, trip) 
                VALUES ('2024-05-20', 'Walmart', 50.25, 'Grocery', NULL, NULL);
        """, language="sql")
        
        st.markdown("**Insert into Income:**")
        st.code("""
                INSERT INTO income (date, amount, source, regular, notes) 
                VALUES ('2024-05-01', 3000.00, 'Salary', TRUE, 'Monthly Pay');
        """, language="sql")

    # --- Date & Text Filters ---
    with st.expander("📅 Date & 🔤 Text Filters"):
        st.markdown("**Filter by Date:**")
        st.code("SELECT * FROM expense WHERE date > '2024-01-01';", language="sql")
        st.code("SELECT * FROM income WHERE date BETWEEN '2024-01-01' AND '2024-03-31';", language="sql")
        
        st.markdown("**Filter by Text (Contains/Like):**")
        st.caption("Use `%` as a wildcard. `ILIKE` is case-insensitive.")
        st.code("SELECT * FROM expense WHERE items LIKE '%Coffee%'; -- Case sensitive", language="sql")
        st.code("SELECT * FROM expense WHERE items ILIKE '%coffee%'; -- Case insensitive", language="sql")