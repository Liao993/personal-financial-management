import streamlit as st # type: ignore
from datetime import date
import time
from modules.expense_input.components.expense_form import expense_form
from modules.expense_input.components.review_data import review_data_print_out
from modules.expense_input.middle_layer.confirmed_data_handling import confirmed_data_handling
from backend.expense_backend import fetch_last_expense_data

st.set_page_config(page_title="Expense Input", page_icon="💸", layout='wide')

edit_mode_form = 'edit_mode_expense'
data_saved_key = 'data_saved_expense'
expense_data_key = 'expense_data'
def expense_input_page():
    st.markdown("<h1 style='color: #2e86c1; text-align: center;'>Please Input Your Expense</h1>", unsafe_allow_html=True)
  
    # Initialize session state variables
    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False
    if expense_data_key not in st.session_state:
        st.session_state[expense_data_key] = {}

    # Show the Form
    if st.session_state[edit_mode_form]:
        expense_form(edit_mode_form, data_saved_key, expense_data_key)  # Get the review button state
  
         
        st.write("---")# Print out the last expense data
        last_expense_data = fetch_last_expense_data()
        if not last_expense_data.empty:
            st.write("Last Expense Data:")
            st.table(last_expense_data)
     

    #Form Not shown after clicking the review button
    else:
        if not st.session_state.get(data_saved_key, False):
         
            reviewed_data = review_data_print_out(expense_data_key, edit_mode_form, data_saved_key) #show the review and get confirm status
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")
            
            if confirm_button:
                confirmed_data_handling(reviewed_data, data_saved_key)
            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        elif st.session_state.get(data_saved_key, True): #moved this part to confirmed_data_handling.py
            st.success("Expense data successfully saved! Moving Back to Input Page")
            time.sleep(3)
            # Reset form-related session state to default for the next input
            st.session_state[expense_data_key] = {  # Reset the dictionary
                "date": date.today(),
                "amount": 100.00,
                "items": "",
                "category": "Food Outside",
                "traveling_category": "None",
                "trip": "None"
            }
            st.session_state[edit_mode_form] = True  # Go back to the input form
            st.session_state[data_saved_key] = False  # Reset the saved state
            st.rerun()
            
if __name__ == "__main__":
    expense_input_page()

