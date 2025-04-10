import streamlit as st # type: ignore
import pandas as pd # type: ignore
from modules.monthly_stats.calculation.saving_formula import calculate_savings # type: ignore
from modules.monthly_stats.components.savingKpi import display_saving_kpis # type: ignore
from modules.monthly_stats.components.goal_form import financial_goals_form
from modules.monthly_stats.charts.monthly_pie import create_expense_pie_chart # type: ignore
from modules.monthly_stats.components.spending_table import display_spending_table # type: ignore
from backend.income_backend import fetch_monthly_income # type: ignore
from backend.expense_backend import fetch_monthly_expenses_with_summary # type: ignore

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
     

          # Fetch expense data with summary_category from the database
          expense_data_with_summary = fetch_monthly_expenses_with_summary(year, month) 
          if not expense_data_with_summary.empty:
            # Not Include traveling spending (using summary_category if appropriate)
            monthly_expense_daily_data = expense_data_with_summary[expense_data_with_summary['category'] != 'Traveling'] # You might want to adjust this based on your summary categories
            monthly_expense = monthly_expense_daily_data['amount'].astype(float).sum()
       

          
            #Saving Calculation
            total_saving = monthly_income - monthly_expense
         
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
              display_spending_table(monthly_expense_daily_data, monthly_income)

          with right_col:
              
              create_expense_pie_chart(monthly_expense, total_saving, travel_saving)
      else:
            st.warning("Please select a goal date to calculate monthly statistics.")
  else:
     st.info("Please provide your financial goals to see monthly statistics.")

  


if __name__ == "__main__":
  monthly_stats_page()