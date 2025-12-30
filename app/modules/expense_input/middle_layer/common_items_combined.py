import streamlit as st # type: ignore

def common_items_combined(expense_common_items, expense_items):
    """
    To get one items only
    """
    
    if expense_common_items != "Not Common Store":
        #trimed_expense_common_items = expense_common_items.upper().replace(" ", "")
        return expense_common_items
    else:
        #trimed_expense_items = expense_items.upper().replace(" ", "")
        return expense_items