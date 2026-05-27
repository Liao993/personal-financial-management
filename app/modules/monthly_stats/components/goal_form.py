import streamlit as st # type: ignore
from datetime import date
from backend.transaction_backend import fetch_last_transaction_data


def financial_goals_form():
    saved_goals = st.session_state.get("financial_goals_data", {})
 
    st.markdown("<h4 style='color: #1f618d; text-align: center;'>Set Your Financial Goals</h4>", unsafe_allow_html=True)
   
    last_transaction_data = fetch_last_transaction_data()
    if not last_transaction_data.empty:
        #get the date and first item of the last transaction data
        last_transaction_date = last_transaction_data['date'].iloc[0]
        st.markdown(f"<p color: #f39c12; style='text-align: center;'>Last Transaction: {last_transaction_date}</p>", unsafe_allow_html=True)
    with st.form("financial_goals") as form:
        # First line: Date and RBC Saving
        col1, col2 = st.columns(2)
        with col1:
            goal_date = st.date_input(
                "Date (Please select the last day of the month you want to note)",
                value=saved_goals.get("goal_date", date.today()),
            )
    
        with col2:
            home_deposit = st.number_input(
                "Home Deposit this month",
                value=float(saved_goals.get("home_deposit", 0.00)),
                format="%.2f",
            )

        # Second line: Saving Goal and Retirement Percentage & Current Unnoted Amount in 10 days notice
        col4, col5, col6 = st.columns(3)
        with col4:
            saving_goal = st.number_input(
                "Saving Goal (Total Amount to Save this Month)",
                min_value=0.0,
                value=float(saved_goals.get("saving_goal", 1000.00)),
                format="%.2f",
            )
        with col5:
            medium_term_amount = st.number_input(
                "Medium Term Amount",
                min_value=0.0,
                value=float(saved_goals.get("medium_term_amount", 500.00)),
                format="%.2f",
            )
        with col6:
            retirement_percentage_options = [100, 80, 70, 60, 50, 30, 20]
            saved_retirement_pct = int(saved_goals.get("retirement_percentage", 0.80) * 100)
            retirement_index = (
                retirement_percentage_options.index(saved_retirement_pct)
                if saved_retirement_pct in retirement_percentage_options
                else 1
            )
            retirement_percentage = st.selectbox(
                "Retirement Percentage (%) of Total Saving",
                retirement_percentage_options,
                index=retirement_index,
            )
        # Third line: Traveling Fund Max and Min
        col7, col8, col9 = st.columns(3)
        with col7:
            emergency_funds = st.number_input(
                "Emergency Saving Amount",
                min_value=0.0,
                value=float(saved_goals.get("emergency_funds", 0.0)),
                format="%.2f",
            )
        with col8:
            travel_fund_max = st.number_input(
                "Traveling Fund Max",
                min_value=0.0,
                value=float(saved_goals.get("travel_fund_max", 400.00)),
                format="%.2f",
            )
        with col9:
            travel_fund_min = st.number_input(
                "Traveling Fund Min",
                min_value=0.0,
                value=float(saved_goals.get("travel_fund_min", 200.00)),
                format="%.2f",
            )

        col10, col11 = st.columns(2)
        with col10:
            submit_button = st.form_submit_button("Save Financial Goals")
        with col11:
            if submit_button:
                st.session_state["financial_goals_data"] = {
                    "goal_date": goal_date,
                    "emergency_funds": emergency_funds,
                    "saving_goal": saving_goal,
                    "retirement_percentage": retirement_percentage / 100.0,
                    "medium_term_amount": medium_term_amount,
                    "travel_fund_max": travel_fund_max,
                    "travel_fund_min": travel_fund_min,
                    "home_deposit": home_deposit,
                }
                st.success("Financial goals saved!")

        return st.session_state.get("financial_goals_data", {})

if __name__ == "__main__":
    financial_goals_form()
