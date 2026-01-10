import streamlit as st # type: ignore

def review_data_print_out(expense_data_key, edit_mode_form, data_saved_key):
    """
    Displays the input data for review and provides Confirm/Edit buttons.
    Returns:
        bool: True if the user clicks Confirm, False otherwise.
    """
    st.subheader("Your Input Information:")
    expense_data = st.session_state.get(expense_data_key, {})
    st.info("Remember to run cashflow unbooked affter clicking submit!")
    st.table(expense_data)
    
    
    return expense_data