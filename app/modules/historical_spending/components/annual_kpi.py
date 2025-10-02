import streamlit as st #type:ignore
import pandas as pd #type:ignore
def annual_kpi(expense, year, income, transaction):
    st.markdown(f"<h2 style='text-align: center;'> {year} Personal Annual Spending Overview</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        total_income = income['total_income'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: orange; text-align: center;'><b>Total Earning</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_income:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>% by Total Earning</b></p>",
            unsafe_allow_html=True,
        )
       
    with col2:
        total_expense = expense['amount'].sum()
        house_sum = transaction[transaction['fund_category'] == 'House']['total_amount'].sum()
        # total_spending = total_expense + house expense
        total_spending = total_expense + house_sum
        spending_pct = int(total_spending) / int(total_income) * 100
        st.markdown(
            f"<p style='font-size: 22px; color: red; text-align: center;'><b>Total Spending</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_spending:.2f}</b></p>"
            f"<p style='font-size: 24px;  text-align: center;'><b>{spending_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
    with col3:
        daily_sum = expense[expense["summary_category"] == "Daily Expenses"]["amount"].sum()
        daily_pct = daily_sum/total_income * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #f1c40f; text-align: center;'><b>Total Daily Expenses</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${daily_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>{daily_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
    with col4:
        house_sum = transaction[transaction['fund_category'] == 'House']['total_amount'].sum()
        house_pct = house_sum/total_income * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #16a085; text-align: center;'><b>Total House</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${house_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>{house_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
   
    with col5:
      grocery_sum = expense[expense["category"] == "Grocery"]['amount'].sum()
      expense['month'] = pd.to_datetime(expense['date']).dt.month
        #get number of unique months
      grocery_month = len(expense['month'].unique())
      grocery_avg = grocery_sum / grocery_month
      grocery_pct = grocery_sum / total_income * 100
      st.markdown(
            f"<p style='font-size: 22px; color: #00ab41; text-align: center;'><b>Avg Monthly Grocery</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${grocery_avg:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>{grocery_pct:.2f}%</b></p>",
          unsafe_allow_html=True,
      )
    with col6:
      retire_sum = transaction[(transaction['fund_category'] == 'Retirement Saving')]['total_amount'].sum()
      retire_pct = retire_sum / total_income * 100
      st.markdown(
            f"<p style='font-size: 22px; color: #1AA7EC; text-align: center;'><b>Retirement Saving</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${retire_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>{retire_pct:.2f}%</b></p>",
          unsafe_allow_html=True,
      )
   

