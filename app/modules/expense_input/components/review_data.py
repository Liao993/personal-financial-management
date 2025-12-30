import streamlit as st # type: ignore

def review_data_print_out(expense_data_key, edit_mode_form, data_saved_key):
    """
    Displays the input data for review and provides Confirm/Edit buttons.
    Returns:
        bool: True if the user clicks Confirm, False otherwise.
    """
    st.subheader("Your Input Information:")
    expense_data = st.session_state.get(expense_data_key, {})
    st.table(expense_data)
    st.write(f"**Date:** {expense_data.get('date', '')}")
    st.write(f"**Items:** {expense_data.get('items', '')}")
    st.write(f"**Amount:** {expense_data.get('amount', '')}")
    st.write(f"**Category:** {expense_data.get('category', '')}")
    st.write(f"**Payment Method:** {expense_data.get('payment_method', '')}")
    st.write(f"**Notes:** {expense_data.get('source_notes', '')}")
    st.write(f"**Traveling Category:** {expense_data.get('traveling_category', 'None')}")
    st.write(f"**Trip:** {expense_data.get('trip', 'None')}")

    
    return expense_data