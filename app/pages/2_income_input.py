import streamlit as st # type: ignore
from datetime import date
from utils.validation import validate_income_data
from backend.income_backend import process_income_data

st.set_page_config(page_title="Enter Income", page_icon="💰")

def income_input_page():
    st.markdown("<h1 style='color: orange;'>Please Input Your Income</h1>", unsafe_allow_html=True)

    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = True

    if st.session_state["edit_mode"]:
        with st.form("income_form"):
            st.markdown("### Date")
            income_date = st.date_input("Date", value=date.today())

            st.markdown("### Amount")
            income_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=1717.85)

            st.markdown("### Source")
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
            st.session_state["edit_mode"] = False
            st.rerun()
    else:
        st.subheader("Your Input Information:")
       
        st.write(f"**Date:** {st.session_state.get('income_date', '')}")
        st.write(f"**Amount:** {st.session_state.get('income_amount', '')}")
        st.write(f"**Source:** {st.session_state.get('income_source', '')}")
        st.write(f"**Regular Income:** {'Yes' if st.session_state.get('income_regular', False) else 'No'}")

        col1, col2 = st.columns(2)
        with col1:
            confirm_button = st.button("Confirm")
        with col2:
            edit_button = st.button("Edit")

        if confirm_button:
            st.info("Data sent for validation and saving...")
            income_data = {
                "date": st.session_state.get('income_date', ''),
                "amount": st.session_state.get('income_amount', ''),
                "source": st.session_state.get('income_source', ''),
                "regular": st.session_state.get('income_regular', False),
            }
            st.write("Data before validation:")
            st.write(income_data)

            if validate_income_data(income_data):
                st.info("Income data is valid, sending to backend for saving...") # Updated message
                process_income_data(income_data)
            else:
                # The errors are already displayed in the validation function
                pass

        if edit_button:
            st.session_state["edit_mode"] = True
            st.rerun()
        

if __name__ == "__main__":
    income_input_page()

