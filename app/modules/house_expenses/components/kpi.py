

# get persoonal income deposit

# 1. Get all  total Mortgage Amount (pct for total Mortgage/total deposit)
# 2. Get all  total Extra Mortgage Amount
# 3. Get all  total Tax Amount
# 4. Get all  total Insurance Amount
# 5. Get all  total energy total (Oil + Electricity)
# 6. Get all  water total & sewage total
import streamlit as st #type:ignore
import pandas as pd #type:ignore
def annual_kpi(expense, transaction):
    st.markdown(f"<h2 style='text-align: center;'> Total House Spending Overview</h2>", unsafe_allow_html=True)
    #get how many from from 2024-02-24 until today
    start_date = pd.to_datetime('2024-02-24')
    end_date = pd.to_datetime('today')

    # Calculate the difference in years and months
    # Adding 1 makes it inclusive of both the start and end months
    months_between = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        house_sum = transaction[transaction['fund_category'] == 'House']['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: orange; text-align: center;'><b>Total Income Deposit</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${house_sum:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>Average Spending</b></p>",
            unsafe_allow_html=True,
        )
       
    with col2:
        total_cost = expense[expense["house_category"] != "Extra Mortgage"]["amount"].sum()
        avg_annual_cost = total_cost / months_between * 12
        st.markdown(
            f"<p style='font-size: 22px; color: red; text-align: center;'><b>Total Spending</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_cost:.2f}</b></p>"
            f"<p style='font-size: 24px;  text-align: center;'><b>${avg_annual_cost:.2f}</b></p>",
            unsafe_allow_html=True,
        )
   
    with col3:
        total_mortgage = expense[expense["house_category"] == "Mortgage"]["amount"].sum()
        avg_annual_mortgage = total_mortgage / months_between * 12
        st.markdown(
            f"<p style='font-size: 22px; color: #f1c40f; text-align: center;'><b>Total Mortgage</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_mortgage:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${avg_annual_mortgage:.2f}</b></p>",
            unsafe_allow_html=True,
        )
   
    with col4:
        regular_maintenance_category = ['Regular Expenses', 'Tax']
        total_maintenance_cost = expense[expense["house_summary_category"].isin(regular_maintenance_category)]['amount'].sum()
        avg_annual_maintenance = total_maintenance_cost / months_between * 12
        st.markdown(
            f"<p style='font-size: 22px; color: #28913F; text-align: center;'><b>Total Maintenance </b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_maintenance_cost:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${avg_annual_maintenance:.2f}</b></p>",
            unsafe_allow_html=True,
        )
  
    
    with col5:
        energy_use_category = ['Electricity', 'Oil']
        total_energy_cost = expense[expense["house_category"].isin(energy_use_category)]['amount'].sum()
        avg_annual_energy = total_energy_cost / months_between * 12
        st.markdown(
            f"<p style='font-size: 22px; color: #1AA7EC; text-align: center;'><b>Total Energy</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${total_energy_cost:.2f}</b></p>"
            f"<p style='font-size: 24px; text-align: center;'><b>${avg_annual_energy:.2f}</b></p>",
            unsafe_allow_html=True,
        )
   
    with col6:
       total_water_cost = expense[expense["house_category"] == "Water & Sewage"]["amount"].sum()
       avg_annual_water = total_water_cost / months_between * 12
       st.markdown(
           f"<p style='font-size: 22px; color: #e74c3c; text-align: center;'><b>Total Water & Sewage</b></p>"
           f"<p style='font-size: 24px; text-align: center;'><b>${total_water_cost:.2f}</b></p>"
           f"<p style='font-size: 24px; text-align: center;'><b>${avg_annual_water:.2f}</b></p>",
           unsafe_allow_html=True,
       )
   
