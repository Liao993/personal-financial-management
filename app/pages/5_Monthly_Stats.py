import streamlit as st # type: ignore
import pandas as pd # type: ignore
from modules.monthly_stats.calculation.saving_formula import calculate_savings # type: ignore
from modules.monthly_stats.components.savingKpi import display_saving_kpis # type: ignore
from modules.monthly_stats.components.goal_form import financial_goals_form
from test.expense_data import create_expense_dataframe # type: ignore 
from modules.monthly_stats.charts.monthly_pie import create_expense_pie_chart # type: ignore
from modules.monthly_stats.components.spending_table import display_spending_table # type: ignore
from backend.income_backend import fetch_monthly_income # type: ignore

st.set_page_config(page_title="Monthly Stats", page_icon="💰", layout="wide")

def monthly_stats_page():
  
  st.markdown("<h1 style='color: lightgreen; text-align: center;'>Monthly Stats</h1>", unsafe_allow_html=True)

  financial_goals = financial_goals_form()

  if financial_goals:

      goal_date = financial_goals.get('goal_date')
      saving_goal = financial_goals.get('saving_goal', 0.0)
      travel_fund_goal = financial_goals.get('travel_fund_max', 0.0)
      min_travel_saving = financial_goals.get('travel_fund_min', 0.0)
      rbc_saving = financial_goals.get('rbc_saving', 100.0)
      retirement_saving_pct = financial_goals.get('retirement_percentage', 1.0)

      if goal_date:
          year = goal_date.year
          month = goal_date.month
          monthly_income = fetch_monthly_income(year, month)
          st.info(f"Monthly Income for {year}-{month:02d}: ${monthly_income:.2f}")

          expense_data = create_expense_dataframe()
          # Not Include traveling spending
          monthly_expense_daily_data = expense_data[expense_data['category'] != 'traveling']
          monthly_expense = monthly_expense_daily_data['price'].sum()
          st.info(monthly_expense)

          #Expense by Category
          home_expense = monthly_expense_daily_data[monthly_expense_daily_data['category'] == 'home']['price'].sum()
          saved_for_love_expense = monthly_expense_daily_data[monthly_expense_daily_data['category'] == 'saved for love']['price'].sum()
          donation_and_gift_expense = monthly_expense_daily_data[monthly_expense_daily_data['category'].isin(['donation', 'gift'])]['price'].sum()
          education_expense = monthly_expense_daily_data[monthly_expense_daily_data['category'] == 'education']['price'].sum()
          daily_expense = monthly_expense - home_expense - saved_for_love_expense - donation_and_gift_expense - education_expense

          spending_data = {
                "Home": home_expense,
                "Saved for Love": saved_for_love_expense,
                "Donation & Gift": donation_and_gift_expense,
                "Education": education_expense,
                "Daily Expense": daily_expense
            }
            #Saving Calculation
          total_saving = monthly_income - monthly_expense 
          st.info(f"Total Saving: ${total_saving:.2f}")

          travel_saving, retirement_saving, medium_term_saving = calculate_savings(
            total_saving, travel_fund_goal, saving_goal, min_travel_saving, rbc_saving, retirement_saving_pct
          )
          st.write("---")
          #Display Saving KPIs
          display_saving_kpis(total_saving, travel_saving, retirement_saving, medium_term_saving, rbc_saving)
          
          st.write(" ")
          st.write(" ")
          left_col, right_col = st.columns(2)

          with left_col:
              display_spending_table(spending_data, monthly_income)

          with right_col:
              
              create_expense_pie_chart(monthly_expense, total_saving)
      else:
            st.warning("Please select a goal date to calculate monthly statistics.")
  else:
     st.info("Please provide your financial goals to see monthly statistics.")

  


if __name__ == "__main__":
  monthly_stats_page()