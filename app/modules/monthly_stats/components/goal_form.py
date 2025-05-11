import streamlit as st # type: ignore
from datetime import date

def financial_goals_form():
    st.markdown("<h4 style='color: #1f618d; text-align: center;'>Set Your Financial Goals</h4>", unsafe_allow_html=True)

    with st.form("financial_goals") as form:
        # First line: Date and RBC Saving
        col1, col2 = st.columns(2)
        with col1:
            goal_date = st.date_input("Date", value=date.today())
        with col2:
            rbc_saving = st.number_input("RBC Saving", min_value=0.0, value=100.0, format="%.2f")

        # Second line: Saving Goal and Retirement Percentage
        col3, col4 = st.columns(2)
        with col3:
            saving_goal = st.number_input("Saving Goal", min_value=0.0, value=1000.00, format="%.2f")
        with col4:
            retirement_percentage_options = [100, 80, 70, 60, 50, 30, 20]
            retirement_percentage = st.selectbox("Retirement Percentage (%)", retirement_percentage_options, index=1) # Default to 80

        # Third line: Traveling Fund Max and Min
        col5, col6 = st.columns(2)
        with col5:
            travel_fund_max = st.number_input("Traveling Fund Max", min_value=0.0, value=400.00, format="%.2f")
        with col6:
            travel_fund_min = st.number_input("Traveling Fund Min", min_value=0.0, value=200.00, format="%.2f")

        col7, col8 = st.columns(2)
        with col7:
            submit_button = st.form_submit_button("Save Financial Goals")
        with col8:
            form_data = {}
            if submit_button:
                form_data['goal_date'] = goal_date
                form_data['rbc_saving'] = rbc_saving
                form_data['saving_goal'] = saving_goal
                form_data['retirement_percentage'] = retirement_percentage / 100.0  # Store as a decimal
                form_data['travel_fund_max'] = travel_fund_max
                form_data['travel_fund_min'] = travel_fund_min
                st.success("Financial goals saved!")

        return form_data

if __name__ == "__main__":
    financial_goals_form()