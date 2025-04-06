import streamlit as st # type: ignore
from datetime import date
from utils.validation import validate_income_data
from backend.income_backend import insert_income_data
from modules.input_pages.income_form import income_input_form
st.set_page_config(page_title="Income Input", page_icon="💰")

edit_mode_form = 'edit_mode_income'
data_saved_key = 'data_saved_income'
review_data_key = 'review_income_data'

def income_input_page():
    st.markdown("<h1 style='color: orange; text-align: center;'>Please Input Your Income</h1>", unsafe_allow_html=True)

    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False
    
    if review_data_key not in st.session_state:
        st.session_state[review_data_key] = {}

    if st.session_state[edit_mode_form]:
       income_input_form(edit_mode_form, review_data_key)
      

    else:
        if not st.session_state.get(data_saved_key, False):
            #the about condition means if data_saved_key is False or not active, then show the confirm and edit buttons
            

            st.subheader("Your Input Information:")
            reviewed_data = st.session_state.get(review_data_key, {})
            st.write(f"**Date:** {reviewed_data.get('date', '')}")
            st.write(f"**Amount:** {reviewed_data.get('amount', '')}")
            st.write(f"**Source:** {reviewed_data.get('source', '')}")
            st.write(f"**Regular Income:** {'Yes' if reviewed_data.get('regular', False) else 'No'}")

        
            #Confirm and Edit buttons
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")

            #Validate Data and Save Data after clicking confirm button
            if confirm_button:
                income_data = reviewed_data
                st.info(income_data)
                if validate_income_data(income_data):
                    insert_income_data(income_data)
                    st.session_state[data_saved_key] = True
                    st.rerun() # Rerun to hide Confirm and Edit buttons
                else:
                    pass
            # Back to form to edit information
            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        # If data is saved, show the option to add more income
        elif st.session_state.get(data_saved_key, True):
            st.success("Income data successfully saved!")
            if st.button("Add More Income"):

                # Reset all form-related session state to default
                st.session_state['date'] = date.today()
                st.session_state['amount'] = 1717.85
                st.session_state['source'] = "Gov"
                st.session_state['regular'] = True
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        

if __name__ == "__main__":
    income_input_page()

