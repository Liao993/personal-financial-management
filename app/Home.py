import streamlit as st # type: ignore

def main():

  st.title("Welcome to the Home Page")
  st.markdown("""
  <p style='font-size: 20px; color: #5dade2;'>
  Here you can navigate to different sections of the app to manage your finances effectively.
  </p>
  <ul style='font-size: 18px; color: #f1c40f;'>
    <li><a href="/Monthly_Income_Input" style='color: #2980b9;'>Input Monthly Income</a> - Enter your monthly income details.</li>
    <li><a href="/Manual_Expense_Input" style='color: #2980b9;'>Input Single Expense</a> - Input Single Expense Spending Manually.</li>
    <li><a href="/Upload_Expense" style='color: #2980b9;'>Upload Your Expense Statement</a> - Upload your bank statement without manual input.</li>
    <li><a href="/Monthly_Calculation" style='color: #2980b9;'>Calculate Monthly Expenses and Savings</a> - Summary of your monthly expenses and savings.</li>
    <li><a href="/Transaction" style='color: #2980b9;'>Make a Transaction</a> - Move your money between different funds or account</li>
    <li><a href="/Historical_Stats" style='color: #2980b9;'>View Historical Statistics</a> - Analyze your financial data over time.</li>
    <li><a href="/Traveling_Spending_Stats" style='color: #2980b9;'>View Traveling Spending Statistics</a> - Analyze your travel-related expenses.</li>
    <li><a href="/Current_Saving_Status" style='color: #2980b9;'>View Current Saving Status</a> - Get an overview of your current savings.</li>
    <li><a href="/Statement_Viewer" style='color: #2980b9;'>View Your Detail Earning, Spending, and Saving</a> - Get a detailed view of your financial activities.</li>

  </ul>
  <p style='font-size: 18px;'>
  You can use the navigation menu on the left to access these sections as well. If you have any questions or need assistance, feel free to reach out through the contact page.
  </p>
 
  """, unsafe_allow_html=True)


if __name__ == "__main__":
  main()