import streamlit as st # type: ignore
from utils.savingFormula import calculate_savings # type: ignore
from utils.forms.monthly_stats_form import financial_goals_form 

st.set_page_config(page_title="Income Input", page_icon="💰")

def monthly_stats_page():
  
  st.markdown("<h1 style='color: green; text-align: center;'>Monthly Stats</h1>", unsafe_allow_html=True)

  total_saving = 500 # You'll likely fetch this 
  financial_goals = financial_goals_form()
  st.write("---")

  if financial_goals:

      st.subheader("Using Financial Goals:")
      date = financial_goals.get('goal_date')
      saving_goal = financial_goals.get('saving_goal', 0.0)
      travel_fund_goal = financial_goals.get('travel_fund_max', 0.0)
      min_travel_saving = financial_goals.get('travel_fund_min', 0.0)
      rbc_saving = financial_goals.get('rbc_saving', 100.0)
      retirement_saving_pct = financial_goals.get('retirement_percentage', 1.0)

      st.write(f"Date from form: {date}")
      st.write(f"Total Saving: ${total_saving:.2f}")
      st.write(f"Travel Fund Goal (Max from form): ${travel_fund_goal:.2f}")
      st.write(f"Saving Goal from form: ${saving_goal:.2f}")
      st.write(f"Min Travel Saving (from form): ${min_travel_saving:.2f}")
      st.write(f"RBC Saving from form: ${rbc_saving:.2f}")
      st.write(f"Retirement Saving Percentage from form: {retirement_saving_pct:.2f}")

      travel_saving, retirement_saving, medium_term_saving = calculate_savings(
        total_saving, 
        travel_fund_goal, 
        saving_goal, 
        min_travel_saving, 
        rbc_saving, 
        retirement_saving_pct
      )
  
      st.write("### Monthly Savings Breakdown")
      st.write(f"Travel Saving: ${travel_saving:.2f}")
      st.write(f"Retirement Saving: ${retirement_saving:.2f}")
      st.write(f"Medium Term Saving: ${medium_term_saving:.2f}")
      st.write(f"RBC Saving: ${rbc_saving:.2f}")

  else:
      st.info("Please fill out and submit the financial goals form.")


  


if __name__ == "__main__":
  monthly_stats_page()