import streamlit as st # type: ignore

def common_items_check(expense_common_items, expense_items):
    """
    Handles the data after the user clicks the Review button.  Stores data in session state.
    """
    
    if expense_common_items != "Not Common Store":
        trimed_expense_common_items = expense_common_items.upper().replace(" ", "")
        return trimed_expense_common_items
    else:
        trimed_expense_items = expense_items.upper().replace(" ", "")
        return trimed_expense_items