import streamlit as st #type:ignore

def single_annual_kpi(data, year, annual_income):
    st.markdown(f"<h2 style='text-align: center;'> {year} Spending Overview</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        total_spending = data['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: red; text-align: center;'><b>Total Spending</b></p>"
            f"<p style='font-size: 26px; text-align: center;'><b>${total_spending:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col2:
        total_income = annual_income
        st.markdown(
            f"<p style='font-size: 22px; color: orange; text-align: center;'><b>Total Earning</b></p>"
            f"<p style='font-size: 26px; text-align: center;'><b>${total_income:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col3:
        spending_percentage = int(total_spending) / int(total_income) * 100
        st.markdown(
            f"<p style='font-size: 22px; color: #f7dc6f; text-align: center;'><b>Spending Percentage</b></p>"
            f"<p style='font-size: 26px;  text-align: center;'><b>{spending_percentage:.2f}%</b></p>",
            unsafe_allow_html=True,
        )
    with col4:
        daily_sum = data[data["summary_category"] == "Daily Expenses"]["amount"].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: #00ab41; text-align: center;'><b>Total Daily Expenses</b></p>"
            f"<p style='font-size: 26px; text-align: center;'><b>${daily_sum:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col5:
        house_sum = data[data["summary_category"] == "House"]['amount'].sum()
        st.markdown(
            f"<p style='font-size: 22px; color: #16a085; text-align: center;'><b>House Spending</b></p>"
            f"<p style='font-size: 26px; text-align: center;'><b>${house_sum:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col6:
      grocery_sum = data[data["category"] == "Grocery"]['amount'].sum()
      grocery_avg = grocery_sum/12
      st.markdown(
          f"<p style='font-size: 22px; color: #1AA7EC; text-align: center;'><b>Avg Monthly Grocery</b></p>"
          f"<p style='font-size: 26px; text-align: center;'><b>${grocery_avg:.2f}</b></p>",
          unsafe_allow_html=True,
      )
