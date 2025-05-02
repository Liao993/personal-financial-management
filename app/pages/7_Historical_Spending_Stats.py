from modules.historical_spending.selected_year import selected_year_choice
from modules.historical_spending.components.single_annual_kpi import single_annual_kpi
from modules.historical_spending.components.bar_chart import create_summary_bar_chart
from modules.historical_spending.components.line_chart import create_line_chart
from backend.expense_backend import fetch_annual_expense
from backend.income_backend import fetch_annual_income
import streamlit as st # type: ignore

st.set_page_config(page_title="Historical Stats", page_icon="💰", layout="wide")

edit_mode = 'regular_edit_mode'
year_select_key = "year_select"
def historical_spending():
    if edit_mode not in st.session_state:
        st.session_state[edit_mode] = True

    if year_select_key not in st.session_state:
        st.session_state[year_select_key] = None

    selected_year = None
    if st.session_state[edit_mode]:
        st.markdown("<h1 style='color: orange; text-align: center;'>Historical Stats</h1>", unsafe_allow_html=True)
        selected_year = selected_year_choice(key=year_select_key)  # Pass the key
        if selected_year:
          st.session_state[year_select_key] = selected_year  # Store using the key
        st.session_state[edit_mode] = False
    else:
        selected_year = st.session_state.get(year_select_key)  # Access using the key

        if selected_year == "All":
            st.info("Next Step")
        elif selected_year is not None:
            all_fetched_expense = fetch_annual_expense(selected_year)
            annual_income = fetch_annual_income(selected_year)

            if (len(all_fetched_expense) == 0) | (annual_income == 0):
                st.warning("No Spending or Annual Income in the selected year")
                if st.button("Choose Again", key="choose_again"):
                    st.session_state[edit_mode] = True
                    st.rerun()
            else:
                single_annual_kpi(all_fetched_expense, selected_year, annual_income)
                col1, col2 = st.columns(2)
                with col1:
                    create_summary_bar_chart(all_fetched_expense)
                with col2:
                    create_line_chart()

if __name__ == "__main__":
    historical_spending()