import streamlit as st # type: ignore
from datetime import date
from utils.validation import validate_income_data
from backend.income_backend import insert_income_data

st.set_page_config(page_title="Income Input", page_icon="💰")

edit_mode_form = 'edit_mode_income'
data_saved_key = 'data_saved_income'
def income_input_page():
    st.markdown("<h1 style='color: orange; text-align: center;'>Please Input Your Income</h1>", unsafe_allow_html=True)

    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False

    if st.session_state[edit_mode_form]:
        with st.form("income_form"):
            income_date = st.date_input("Date", value=date.today())

            income_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=1717.85)
   
            source_options = ["Gov", "Tax Return", "Other"]
            selected_source = st.selectbox("Source", source_options)
            income_source = selected_source


            income_regular = st.checkbox("Regular Income", value=True)

            review_button = st.form_submit_button("Review")

        if review_button:
            
            st.session_state["income_date"] = income_date
            st.session_state["income_amount"] = income_amount
            st.session_state["income_source"] = income_source
            st.session_state["income_regular"] = income_regular
            st.session_state[edit_mode_form] = False
            st.session_state[data_saved_key] = False
            st.rerun()

    else:
        st.subheader("Your Input Information:")
       
        st.write(f"**Date:** {st.session_state.get('income_date', '')}")
        st.write(f"**Amount:** {st.session_state.get('income_amount', '')}")
        st.write(f"**Source:** {st.session_state.get('income_source', '')}")
        st.write(f"**Regular Income:** {'Yes' if st.session_state.get('income_regular', False) else 'No'}")

        if not st.session_state.get(data_saved_key, False):
            #the about condition means if data_saved_key is False or not active, then show the confirm and edit buttons
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")

            if confirm_button:
                income_data = {
                    "date": st.session_state.get('income_date', ''),
                    "amount": st.session_state.get('income_amount', ''),
                    "source": st.session_state.get('income_source', ''),
                    "regular": st.session_state.get('income_regular', False),
                }

                if validate_income_data(income_data):
                    insert_income_data(income_data)
                    st.success("Income data successfully saved!")
                    st.session_state[data_saved_key] = True
                    st.rerun() # Rerun to hide Confirm and Edit buttons
                else:
                    pass

            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        if st.session_state.get(data_saved_key, True):
            if st.button("Add More Income"):
                # Reset all form-related session state to default
                st.session_state['income_date'] = date.today()
                st.session_state['income_amount'] = 1717.85
                st.session_state['income_source'] = "Gov"
                st.session_state['income_regular'] = True
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        

if __name__ == "__main__":
    income_input_page()

