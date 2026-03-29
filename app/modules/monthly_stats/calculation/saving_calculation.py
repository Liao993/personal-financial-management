import streamlit as st # type: ignore
from datetime import datetime
from backend.income_backend import fetch_monthly_income # type: ignore
from backend.expense_backend import fetch_monthly_expenses_with_summary # type: ignore
from modules.monthly_stats.calculation.saving_formula import savings_formula # type: ignore

#calculate the monthly spending and saving based on the financial goals
def expense_and_saving_calculation(financial_goals):
    
    #financial goals data recevied from financial_goals_form
    goal_date = financial_goals.get('goal_date')
    saving_goal = financial_goals.get('saving_goal', 0.0)
    travel_fund_goal = financial_goals.get('travel_fund_max', 0.0)
    min_travel_saving = financial_goals.get('travel_fund_min', 0.0)
    emergency_funds = financial_goals.get('emergency_funds', 0.0)
    retirement_saving_pct = financial_goals.get('retirement_percentage', 1.0)
    medium_term_amount = financial_goals.get('medium_term_amount', 0.0)
    home_deposit_amount = financial_goals.get('home_deposit', 0.0)

    if goal_date:
        # Get the Monthly Income
        monthly_income = fetch_monthly_income(goal_date.year, goal_date.month)
        # Get the Monthly Expense
        expense_data_with_summary = fetch_monthly_expenses_with_summary(goal_date.year, goal_date.month) 

        if not expense_data_with_summary.empty:
          # Not Include traveling spending (using summary_category if appropriate)
            monthly_expense_daily_data = expense_data_with_summary[expense_data_with_summary['category'] != 'Traveling'] 
            monthly_expense = monthly_expense_daily_data['amount'].astype(float).sum()
        
            #Total Saving Calculation
            total_saving = monthly_income - monthly_expense - home_deposit_amount

            # Calculate more detailed saving breakdown
            travel_saving, retirement_saving, medium_term_saving = savings_formula(
              total_saving, travel_fund_goal, saving_goal, min_travel_saving, emergency_funds, retirement_saving_pct, medium_term_amount
            )

        else:
          st.warning("No expense data available for the selected month. Please check your records.")
    else:
      st.warning("Please select a goal date to calculate monthly statistics.")

    return goal_date, total_saving, travel_saving, retirement_saving, medium_term_saving, emergency_funds, monthly_expense_daily_data, monthly_income, monthly_expense, home_deposit_amount