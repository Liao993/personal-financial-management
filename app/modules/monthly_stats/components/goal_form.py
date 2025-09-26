import streamlit as st # type: ignore
from datetime import date
from backend.transaction_backend import fetch_last_transaction_data
from utils.data import unoted_amount_in_EQ
def financial_goals_form():
   
 
    st.markdown("<h4 style='color: #1f618d; text-align: center;'>Set Your Financial Goals</h4>", unsafe_allow_html=True)
   
    last_transaction_data = fetch_last_transaction_data()
    if not last_transaction_data.empty:
        #get the date and first item of the last transaction data
        last_transaction_date = last_transaction_data['date'].iloc[0]
        st.markdown(f"<p color: #f39c12; style='text-align: center;'>Last Transaction: {last_transaction_date}</p>", unsafe_allow_html=True)
    with st.form("financial_goals") as form:
        # First line: Date and RBC Saving
        col1, col2, col3 = st.columns(3)
        with col1:
            goal_date = st.date_input("Date (Please select the last day of the month you want to note)", value=date.today()) 
        with col2:
            unnoted_amount_in_10_days_notice = st.number_input("Current Amount in 10 days notice", value=unoted_amount_in_EQ, format="%.2f")
        with col3:
            home_deposit = st.number_input("Home Deposit this month", value=500.00, format="%.2f")

        # Second line: Saving Goal and Retirement Percentage & Current Unnoted Amount in 10 days notice
        col4, col5, col6 = st.columns(3)
        with col4:
            saving_goal = st.number_input("Saving Goal (Total Amount to Save this Month)", min_value=0.0, value=1000.00, format="%.2f")
        with col5:
            medium_term_amount = st.number_input("Medium Term Amount", min_value=0.0, value=500.00, format="%.2f")
        with col6:
            retirement_percentage_options = [100, 80, 70, 60, 50, 30, 20]
            retirement_percentage = st.selectbox("Retirement Percentage (%) of Total Saving", retirement_percentage_options, index=1) # Default to 80
        # Third line: Traveling Fund Max and Min
        col7, col8, col9 = st.columns(3)
        with col7:
            rbc_saving = st.number_input("RBC Saving Amount", min_value=0.0, value=100.0, format="%.2f")
        with col8:
            travel_fund_max = st.number_input("Traveling Fund Max", min_value=0.0, value=400.00, format="%.2f")
        with col9:
            travel_fund_min = st.number_input("Traveling Fund Min", min_value=0.0, value=200.00, format="%.2f")

        col10, col11 = st.columns(2)
        with col10:
            submit_button = st.form_submit_button("Save Financial Goals")
        with col11:
            form_data = {}
            if submit_button:
                form_data['goal_date'] = goal_date
                form_data['rbc_saving'] = rbc_saving
                form_data['saving_goal'] = saving_goal
                form_data['retirement_percentage'] = retirement_percentage / 100.0  # Store as a decimal
                form_data['medium_term_amount'] = medium_term_amount
                form_data['travel_fund_max'] = travel_fund_max
                form_data['travel_fund_min'] = travel_fund_min
                form_data['unnoted_amount_in_10_days_notice'] = unnoted_amount_in_10_days_notice
                form_data['home_deposit'] = home_deposit
                st.success("Financial goals saved!")

        return form_data

if __name__ == "__main__":
    financial_goals_form()