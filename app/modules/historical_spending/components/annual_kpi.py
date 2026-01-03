import streamlit as st #type:ignore
import pandas as pd #type:ignore
from decimal import Decimal
def annual_kpi(year, expense, income, transaction):
    st.markdown(f"<h2 style='text-align: center;'> {year} Personal Annual Spending Overview</h2>", unsafe_allow_html=True)
    expense['month'] = pd.to_datetime(expense['date']).dt.month
    unique_month = Decimal(expense['month'].nunique())
    
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:

        st.markdown(
            f"<p style='font-size: 22px; text-align: center;'><b>Category</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>Total</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>Average</b></p>"
            f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
            f"<p style='font-size: 24px; text-align: center;'><b>% by Income</b></p>",
            unsafe_allow_html=True,
        )
    with col2:
        total_income = income['total_income'].sum()
        average_income = income['total_income'].mean()
        st.markdown(
            f"<p style='font-size: 22px; color: orange; text-align: center;'><b>Earning</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_income:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${average_income:.2f}</b></p>"
            f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
            f"<p style='font-size: 24px; text-align: center;'><b>100%</b></p>",
            unsafe_allow_html=True,
        )
       
    with col3:
        
        total_expense = expense['amount'].sum()
        house_sum = transaction[transaction['fund_category'] == 'House']['total_amount'].sum()
        # total_spending = total_expense + house expense
        total_spending = total_expense + house_sum
        average_total_spending = total_spending / unique_month
        spending_pct = int(total_spending) / int(total_income) * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #e74c3c; text-align: center;'><b>All Spending</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_spending:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${average_total_spending:.2f}</b></p>"
            f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
            f"<p style='font-size: 24px;  text-align: center;'><b>{spending_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
    with col4:
        daily_sum = expense[expense["summary_category"] == "Daily Expenses"]["amount"].sum()
        average_daily_sum = daily_sum / unique_month

        daily_pct = daily_sum/total_income * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #f1c40f; text-align: center;'><b>Daily Expenses</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${daily_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${average_daily_sum:.2f}</b></p>"
            f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
            f"<p style='font-size: 24px; text-align: center;'><b>{daily_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )

    with col5:
        house_sum = transaction[transaction['fund_category'] == 'House']['total_amount'].sum()
        average_house_sum = house_sum / unique_month

        house_pct = house_sum/total_income * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #bce784; text-align: center;'><b>House</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${house_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${average_house_sum:.2f}</b></p>"
            f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
            f"<p style='font-size: 24px; text-align: center;'><b>{house_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
    with col6:
        offering_sum = expense[expense["summary_category"] == "Donation and Gifts"]["amount"].sum()
        average_offering_sum = offering_sum / unique_month

        offering_pct = offering_sum/total_income * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #989fce; text-align: center;'><b>Offerings</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${offering_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${average_offering_sum:.2f}</b></p>"
            f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
            f"<p style='font-size: 24px; text-align: center;'><b>{offering_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
   
    with col7:
        grocery_sum = expense[expense["category"] == "Grocery"]['amount'].sum()
        grocery_avg = grocery_sum / unique_month
        grocery_pct = grocery_sum / total_income * 100
        st.markdown(
                f"<p style='font-size: 22px; color: #ff8fab; text-align: center;'><b>Grocery</b></p>"
                f"<p style='font-size: 24px; text-align: center;'><b>${grocery_sum:.2f}</b></p>"
                f"<p style='font-size: 24px; text-align: center;'><b>${grocery_avg:.2f}</b></p>"
                f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
                f"<p style='font-size: 24px; text-align: center;'><b>{grocery_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
    with col8:
        retire_sum = transaction[(transaction['fund_category'] == 'Retirement Saving')]['total_amount'].sum()
        average_retire_sum = retire_sum / unique_month

        retire_pct = retire_sum / total_income * 100
        st.markdown(
                f"<p style='font-size: 22px; color: #1AA7EC; text-align: center;'><b>Retirement Saving</b></p>"
                f"<p style='font-size: 24px; text-align: center;'><b>${retire_sum:.2f}</b></p>"
                f"<p style='font-size: 24px; text-align: center;'><b>${average_retire_sum:.2f}</b></p>"
                f"<hr style='border: none; border-top: 2px dashed #bbb; margin: 20px 0;'>"
                f"<p style='font-size: 24px; text-align: center;'><b>{retire_pct:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
   

