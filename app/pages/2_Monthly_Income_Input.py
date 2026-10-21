import streamlit as st # type: ignore
from utils.validation import validate_income_data
from backend.income_backend import insert_income_data, fetch_last_income_data
from modules.income_input.income_form import income_input_form
from modules.income_input.income_review import review_income_input

st.set_page_config(page_title="Income Input", page_icon="💰", layout='wide')

edit_mode_form = 'edit_mode_income'
data_saved_key = 'data_saved_income'
review_data_key = 'review_income_data'


def reset_income_input_state():
    st.session_state.pop(review_data_key, None)
    st.session_state["income_form_version"] = (
        st.session_state.get("income_form_version", 0) + 1
    )
    st.session_state[edit_mode_form] = True
    st.session_state[data_saved_key] = False


def income_input_page():
    st.markdown("<h1 style='color: #f39c12; text-align: center;'>Please Input Your Income</h1>", unsafe_allow_html=True)
   
    # form shown or not
    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    # data saved or not
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False
    # catch review data
    if review_data_key not in st.session_state:
        st.session_state[review_data_key] = {}

    if st.session_state.pop("income_success_message", None):
        st.success("Income data successfully saved.")
    
    # if it is in edit mode, show the form
    if st.session_state[edit_mode_form]:
       income_input_form(edit_mode_form, review_data_key)

       st.write("---")  # Print out the last income data
       last_income_data = fetch_last_income_data()
       if not last_income_data.empty:
           st.write("Last Income Data:")
           st.table(last_income_data)
      
    else:
       
        if not st.session_state.get(data_saved_key, False):
            #the about condition means if data_saved_key is False or not active, then show the confirm and edit buttons
            
            # Show input information for review
            reviewed_data = review_income_input(review_data_key)

            #Confirm and Edit buttons
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
                
            with col2:
                edit_button = st.button("Edit")

            #Validate Data and Save Data after clicking confirm button
            if confirm_button:
                income_data = reviewed_data
                
                if validate_income_data(income_data):
                    insert_income_data(income_data)
                    st.session_state[data_saved_key] = True
                    st.success("Transaction recorded successfully!")
                    st.rerun() # Rerun to hide Confirm and Edit buttons

            # Back to form to edit information
            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        # If data is saved, show the option to add more income
        elif st.session_state.get(data_saved_key, True):
            st.session_state["income_success_message"] = True
            reset_income_input_state()
            st.rerun()

if __name__ == "__main__":
    income_input_page()
