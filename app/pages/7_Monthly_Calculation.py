import streamlit as st # type: ignore
import pandas as pd # type: ignore
from datetime import datetime # type: ignore

from modules.monthly_stats.components.savingKpi import display_saving_kpis # type: ignore
from modules.monthly_stats.components.goal_form import financial_goals_form
from modules.monthly_stats.components.monthly_pie import create_expense_pie_chart # type: ignore
from modules.monthly_stats.components.spending_table import display_spending_table # type: ignore
from modules.monthly_stats.middle_layer.monthly_saving import monthly_savings_action
from modules.monthly_stats.calculation.saving_calculation import expense_and_saving_calculation # type: ignore


st.set_page_config(page_title="Monthly Stats", page_icon="💰", layout="wide")


def monthly_stats_page():
    """
    Displays monthly statistics, including a form for financial goals,
    calculation results, and a button to save the results.
    """
    st.markdown("<h1 style='color: #a9cce3; text-align: center;'>Monthly Stats</h1>", unsafe_allow_html=True)

    financial_goals = financial_goals_form()

    if financial_goals:
        # calculate the monthly spending and saving if I got the financial goals
        goal_date, total_saving, travel_saving, retirement_saving, medium_term_saving, rbc_saving, \
        monthly_expense_daily_data, monthly_income, monthly_expense, \
            unnoted_amount_in_EQ, unnoted_amount_in_RBC, home_deposit_amount = expense_and_saving_calculation(
            financial_goals)

        # Store calculated values in session state
        st.session_state['goal_datetime'] = goal_date
        st.session_state['source_notes'] = f"saved from {goal_date.year} {goal_date.month:02d}"  # added formatting for month
        st.session_state['travel_saving'] = travel_saving
        st.session_state['retirement_saving'] = retirement_saving
        st.session_state['medium_term_saving'] = medium_term_saving
        st.session_state['rbc_saving'] = rbc_saving
        st.session_state['unnoted_amount_in_EQ'] = unnoted_amount_in_EQ
        st.session_state['unnoted_amount_in_RBC'] = unnoted_amount_in_RBC
        st.session_state['home_deposit'] = home_deposit_amount

        # Display the spending and saving results
        st.write("---")
        # Display Saving KPIs
        display_saving_kpis(total_saving, travel_saving, retirement_saving, medium_term_saving, rbc_saving, unnoted_amount_in_EQ, unnoted_amount_in_RBC)

        st.write(" ")
        st.write(" ")
        left_col, right_col = st.columns(2)

        with left_col:
            # Display the spending table and Save the Results button
            display_spending_table(monthly_expense_daily_data, monthly_income, home_deposit_amount)
            st.write(" ")
            st.write(" ")
            if st.button("Save Your Results", on_click=monthly_savings_action):
                pass

        with right_col:
            create_expense_pie_chart(monthly_expense, total_saving, travel_saving, home_deposit_amount)

  


if __name__ == "__main__":
  monthly_stats_page()