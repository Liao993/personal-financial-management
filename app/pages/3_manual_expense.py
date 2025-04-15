import streamlit as st # type: ignore
from datetime import date
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data
from utils.css import drop_down_list
st.set_page_config(page_title="Expense Input", page_icon="💸")

edit_mode_form = 'edit_mode_expense'
data_saved_key = 'data_saved_expense'
category_options = ["Grocery", "Food Outside", "Household Goods", "Cell Phone", "Gas", "Donation", "Gifts", "Home Deposit", "Medicine", "Saved for Love", "Transportation", "Education", "Traveling" , "Fun / Tickets", "Clothing", "Liquar", "Others"]

def expense_input_page():
    st.markdown("<h1 style='color: lightblue; text-align: center;'>Please Input Your Expense</h1>", unsafe_allow_html=True)

    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False

    if st.session_state[edit_mode_form]:
        with st.form("expense_form"):
  
            expense_date = st.date_input("Date", value=date.today())


            expense_items = st.text_input("Items")

 
            expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=100.00)

            
            selected_category = st.selectbox("Category", category_options)

            # to all small characters
            expense_category = selected_category

            notes = st.text_input("Notes", "")

            drop_down_list()


            review_button = st.form_submit_button("Review")

        if review_button:
            st.session_state["expense_date"] = expense_date
            st.session_state["expense_items"] = expense_items
            st.session_state["expense_amount"] = expense_amount
            st.session_state["expense_category"] = expense_category
            st.session_state["notes"] = notes
            st.session_state[edit_mode_form] = False
            st.session_state[data_saved_key] = False
            st.rerun()

    else:
        
        if not st.session_state.get(data_saved_key, False):
            #the about condition means if data_saved_key is False or not active, then show the confirm and edit buttons

            st.subheader("Your Input Information:")
       
            st.write(f"**Date:** {st.session_state.get('expense_date', '')}")
            st.write(f"**Items:** {st.session_state.get('expense_items', '')}")
            st.write(f"**Amount:** {st.session_state.get('expense_amount', '')}")
            st.write(f"**Category:** {st.session_state.get('expense_category', '')}")
            st.write(f"**Notes:** {st.session_state.get('notes', '')}")
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")

            if confirm_button:
                expense_data = {
                    "date": st.session_state.get('expense_date', ''),
                    "amount": st.session_state.get('expense_amount', ''),
                    "items": st.session_state.get('expense_items', ''),
                    "category": st.session_state.get('expense_category', ''),
                    "notes": st.session_state.get('notes', ''),
                }

                if validate_expense_data(expense_data):
                    insert_expense_data(expense_data)
                   
                    st.session_state[data_saved_key] = True
                    st.rerun() # Rerun to hide Confirm and Edit buttons
                else:
                    pass

            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        if st.session_state.get(data_saved_key, True):
            st.success("Expense data successfully saved!")
            if st.button("Add More Expense"):
                # Reset all form-related session state to default
                st.session_state['expense_date'] = date.today()
                st.session_state['expense_amount'] = 100
                st.session_state['expense_items'] = ""
                st.session_state['expense_category'] = ""
                st.session_state['notes'] = ""
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        

if __name__ == "__main__":
    expense_input_page()

