import streamlit as st # type: ignore

def main():

  st.title("Welcome to the Home Page")

  st.markdown("""
  <p style='font-size: 24px; color: #5dade2;'>
    Bookeeping Actual Money Usage Insturctions.
  </p>
  <table>
  <thead>
  <tr>
    <th>Money Category</th>
    <th>Bookkeeping / Note</th>
    <th>Actual Payment Source</th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td>Earning</td>
    <td>Noted as Income.</td>
    <td>Calculated through monthly calculations</td>
  </tr>
  <tr>
    <td>House Expense</td>
    <td>Noted in the Excel (not this application).</td>
    <td>TD</td>
  </tr>
  <tr>
    <td>Traveling Spending</td>
    <td>Noted as a withdrawal from Traveling Funds.</td>
    <td>RBC Chequing or EQ Notice Account</td>
  </tr>
  <tr>
    <td>Monthly Expenses</td>
    <td>Calculated monthly. Unnoted spending is noted as the spending of the next month.</td>
    <td>RBC Chequing</td>
  </tr>
  <tr>
    <td>Spending from Medium-term Saving</td>
    <td>Noted as a withdrawal from Medium-term Saving Funds.</td>
    <td>RBC Chequing or EQ Notice Account</td>
  </tr>
  </tbody>
  </table>
  <p style='font-size: 24px; color: #5dade2;'>
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
 

 
  """, unsafe_allow_html=True)


if __name__ == "__main__":
  main()