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
    rbc_saving = financial_goals.get('rbc_saving', 100.0)
    retirement_saving_pct = financial_goals.get('retirement_percentage', 1.0)
    medium_term_amount = financial_goals.get('medium_term_amount', 0.0)
    unnoted_amount_in_10_days_notice = financial_goals.get('unnoted_amount_in_10_days_notice', 0.0)

    if goal_date:
        # Get the Monthly Income
        monthly_income = fetch_monthly_income(goal_date.year, goal_date.month)
        # Get the Monthly Expense
        expense_data_with_summary = fetch_monthly_expenses_with_summary(goal_date.year, goal_date.month) 

        if not expense_data_with_summary.empty:
          # Not Include traveling spending (using summary_category if appropriate)
            monthly_expense_daily_data = expense_data_with_summary[expense_data_with_summary['category'] != 'Traveling'] # You might want to adjust this based on your summary categories
            monthly_expense = monthly_expense_daily_data['amount'].astype(float).sum()
        
            #Total Saving Calculation
            total_saving = monthly_income - monthly_expense

            # Calculate more detailed saving breakdown
            travel_saving, retirement_saving, medium_term_saving = savings_formula(
              total_saving, travel_fund_goal, saving_goal, min_travel_saving, rbc_saving, retirement_saving_pct, medium_term_amount
            )

            # Calculate unnoted amount 
            unnoted_amount_in_EQ = round(unnoted_amount_in_10_days_notice, 2)
            unnoted_amount_in_RBC = round(travel_saving+retirement_saving+medium_term_saving-unnoted_amount_in_EQ, 2)
        else:
          st.warning("No expense data available for the selected month. Please check your records.")
    else:
      st.warning("Please select a goal date to calculate monthly statistics.")

    return goal_date, total_saving, travel_saving, retirement_saving, medium_term_saving, rbc_saving, monthly_expense_daily_data, monthly_income, monthly_expense, unnoted_amount_in_EQ, unnoted_amount_in_RBC