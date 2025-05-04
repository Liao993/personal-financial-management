import streamlit as st # type: ignore
from datetime import date
import time
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data
from utils.css import drop_down_list
from utils.data import expense_category_options, common_store_list, traveling_category_options, trip_destination
from Home import main
st.set_page_config(page_title="Expense Input", page_icon="💸")

edit_mode_form = 'edit_mode_expense'
data_saved_key = 'data_saved_expense'


def expense_input_page():
    st.markdown("<h1 style='color: lightblue; text-align: center;'>Please Input Your Expense</h1>", unsafe_allow_html=True)

    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False

    if st.session_state[edit_mode_form]:
        with st.form("expense_form"):
  
            expense_date = st.date_input("Date", value=date.today())

            expense_common_items = st.selectbox("Items", common_store_list, key="common_item_select")
            expense_items = st.text_input("Items (if not in common store list)", key="custom_item_input")
            
 
            expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=100.00)

            
            selected_category = st.selectbox("Category", expense_category_options)

            traveling = st.selectbox("Traveling Category", ["None"] + traveling_category_options)

            trip = st.selectbox("Trip", ["None"] + trip_destination)

            # to all small characters
            expense_category = selected_category


            drop_down_list()


            review_button = st.form_submit_button("Review")

        if review_button:
            st.session_state["expense_date"] = expense_date

            if st.session_state.get("common_item_select") != "Not Common Store":
                trimed_expense_common_items = expense_common_items.upper().replace(" ", "")
                st.session_state["expense_items"] = trimed_expense_common_items
             
            else:
                trimed_expense_items = expense_items.upper().replace(" ", "")
                st.session_state["expense_items"] = trimed_expense_items
             

            st.session_state["expense_amount"] = expense_amount
            st.session_state["expense_category"] = expense_category
            st.session_state["traveling_category"] = traveling
            st.session_state["trip"] = trip

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
            st.write(f"**Traveling Category:** {st.session_state.get('traveling_category', 'None')}")
            st.write(f"**Trip:** {st.session_state.get('trip', 'None')}")

            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")

            if confirm_button:
                expense_data = {
                    "date": st.session_state.get('expense_date', ''),
                    "items": st.session_state.get('expense_items', ''),
                    "amount": st.session_state.get('expense_amount', ''),
                    "category": st.session_state.get('expense_category', ''),
                    "traveling_category": st.session_state.get('traveling_category', None) if st.session_state.get('traveling_category') != "None" else None,
                    "trip": st.session_state.get('trip', None) if st.session_state.get('trip') != "None" else None,
                }

                if validate_expense_data(expense_data):
                    st.info("Data is saving to database .......")
                    time.sleep(3)
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
            st.success("Expense data successfully saved! Moving Back to Input Page")
            time.sleep(3)
            # Reset form-related session state to default for the next input
            st.session_state['expense_date'] = date.today()
            st.session_state['expense_amount'] = 100.0
            st.session_state['expense_items'] = ""
            st.session_state['expense_category'] = "Grocery"
            st.session_state['traveling_category'] = "None"
            st.session_state['trip'] = "None"
            st.session_state[edit_mode_form] = True # Go back to the input form
            st.session_state[data_saved_key] = False # Reset the saved state
            st.rerun()
if __name__ == "__main__":
    expense_input_page()

