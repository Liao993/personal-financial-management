import streamlit as st # type: ignore

def main():
  #made it wide
  st.set_page_config(page_title="Home", page_icon="💸", layout='wide')
  st.title("Welcome to the Home Page")

  st.markdown("""
  <p style='font-size: 24px; color: #5dade2;'>
    Bookeeping and Actual Money Usage Insturctions.
  </p>
  <ui style='font-size: 18px;'>
  <li>Any earning, not matter regular or sudden huge earning, should be recorded with Income Input, and then Distributed with Monthly Calculations.</li>
  <li>Two ways to record expense, Manual Expense Input and Upload Statement.</li>
  <li>Record withdrawl in Cashflow Ubooked after recording any expense (Manuall or Statement), and <b style='color:#e74c3c;'>seperated them by month.</b></li>
  <li>Any Money Transfer to Saving Account before bookkeeping should be recorded in Cashflow Unbooked as transfer between accounts.</li>
  <li>Record Fund Transaction based on fund categoery after Monthly Calculations to make sure the money is in the right place.</li>
  <li>If any Money need to withdraw from Saving Account, please record the withdrawl in Cashflow Unbooked, not transfer between accounts.</li>
  </ul>
  """, unsafe_allow_html=True)

  st.divider()

  st.markdown("""
 

 
  <p style='font-size: 24px; color: #5dade2;'>
  Here you can navigate to different sections of the app to manage your finances effectively.
  </p>
  <ul style='font-size: 18px; color: #f1c40f;'>
    <li><a href="/Monthly_Income_Input" style='color: #2980b9;'>Input Monthly Income</a> - Enter your monthly income details.</li>
    <li><a href="/Manual_Expense_Input" style='color: #2980b9;'>Input Single Expense</a> - Input Single Expense Spending Manually.</li>
    <li><a href="/Upload_Expense" style='color: #2980b9;'>Upload Your Expense Statement</a> - Upload your bank statement without manual input.</li>
    <li><a href="/Cashflow_Unbooked" style='color: #2980b9;'>Trace Cashflow Before Bookkeeping</a> - Money Move in is Earning, Moeny Move out is Expense, based on <b style='color:#e74c3c;'>actual account</b>.</li>
    <li><a href="/Monthly_Calculation" style='color: #2980b9;'>Calculate Monthly Expenses and Savings</a> - Summary of your monthly expenses and savings.</li>
    <li><a href="/Transaction" style='color: #2980b9;'>Make a Transaction</a> - Money move in and out is based on <b style='color:#e74c3c;'>fund category, not actual account</b>.</li>
    <li><a href="/Historical_Stats" style='color: #2980b9;'>View Historical Statistics</a> - Analyze your financial data over time.</li>
    <li><a href="/Traveling_Spending_Stats" style='color: #2980b9;'>View Traveling Spending Statistics</a> - Analyze your travel-related expenses.</li>
    <li><a href="/Current_Saving_Status" style='color: #2980b9;'>View Current Saving Status</a> - Get an overview of your current savings.</li>
    <li><a href="/Statement_Viewer" style='color: #2980b9;'>View Your Detail Earning, Spending, and Saving</a> - Get a detailed view of your financial activities.</li>

  </ul>
 

 
  """, unsafe_allow_html=True)




if __name__ == "__main__":
  main()