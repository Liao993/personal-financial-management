import streamlit as st # type: ignore
from utils.data import expense_category_options, transaction_type_database, fund_categories,traveling_category_options,account_name_list 

def table_hint():
    
    st.subheader("📚 SQL Syntax Guide & Hints")
    # --- Table and Fields Section ---
    with st.expander("📚 Table and Fields (Schema Cheat Sheet)"):
        
        # Helper function to style text in markdown
        def style_text(text, color):
            return f"<span style='color: {color}; font-weight: bold;'>{text}</span>"

        # --- EXPENSE TABLE ---
        with st.expander("💸 expense Table"):
            columns = style_text("id, date, amount, items, category, traveling_category, trip", "orange")
            dbt_columns = style_text(":summary_category", "lightblue")
            st.markdown(f"**Columns:** {columns}", unsafe_allow_html=True)
            st.markdown(f"**Intermediate Columns** (from `dbt_budget.intermediate_expenses_with_summary`): {dbt_columns}", unsafe_allow_html=True)
            
            options_expense = style_text(', '.join(expense_category_options), "pink")
            st.markdown(f"**Expense category options:** {options_expense}", unsafe_allow_html=True) 
            
            options_travel = style_text(', '.join(traveling_category_options), "pink")
            st.markdown(f"**Traveling category options:** {options_travel}", unsafe_allow_html=True)      

        # --- INCOME TABLE ---
        with st.expander("💰 income Table"):
            columns = style_text("id, date, amount, source, regular, notes", "orange")
            st.markdown(f"**Columns:** {columns}", unsafe_allow_html=True)

        # --- TRANSACTIONS TABLE ---
        with st.expander("📈 transactions Table"):
            columns = style_text("transaction_id, date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account", "orange")
            st.markdown(f"**Columns:** {columns}", unsafe_allow_html=True)
            
            options_type = style_text(', '.join(transaction_type_database), "pink")
            st.markdown(f"**Transaction type options:** {options_type}", unsafe_allow_html=True)
            
            options_account = style_text(', '.join(account_name_list), "pink")
            st.markdown(f"**Account name options:** {options_account}", unsafe_allow_html=True)
            
            options_fund = style_text(', '.join(fund_categories), "pink")
            st.markdown(f"**Fund category options:** {options_fund}", unsafe_allow_html=True)
