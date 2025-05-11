import streamlit as st # type: ignore

def selected_year_choice_form():
    with st.form("historical_years") as form:
      year_list = [2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035]
      col1, col2 = st.columns(2)
      with col1:
            st.markdown("<h1 style='color: #f1c40f; text-align: center;'>Historical Annual Balance Stats</h1>", unsafe_allow_html=True)
      with col2:
        selected_year = st.selectbox("Please select a year", year_list)
        submit_button = st.form_submit_button("Submit")
         
    

      if submit_button:
        return selected_year

      