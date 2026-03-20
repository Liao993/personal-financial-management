import streamlit as st # type: ignore

def main():
  #made it wide
  st.set_page_config(page_title="Home", page_icon="💸", layout='wide')


  st.markdown("""
  <p style='font-size: 40px; text-align: center; color: #5dade2;'>Personal Finance Management</p>
  <ui style='font-size: 20px;'>
  <b style='color:#f1c40f; font-size: 24px;'>Income Rules</b>           
  <li> Any <b style='color:#e74c3c;'>earning</b>, not matter regular or sudden huge earning, should be recorded with  <b style='color:#5dade2;'>Income Input</b>, and then Distributed with Monthly Calculations.</li>
  <hr/>           
  <b style='color:#f1c40f; font-size: 24px;'>Expense Rules</b>  
  <li>If expense is <b style='color:#e74c3c;'>monthly daily expense</b>, Use Manual Expense Input and Upload Statement.</li>  
  <li> House expense should be recorded as <b style='color:#5dade2;'>House Deposit in Transaction.</b></li>
  <li> <b style='color:#5dade2;'>Prepaid</b> expense should NOT be recorded as <b style='color:#5dade2;'>Expense.</b></li>

  <hr/>
  <b style='color:#f1c40f; font-size: 24px;'>Transaction Rules</b> 
  <li> The <b style='color:#e74c3c;'>Monthly Saving and House </b> should be recorded via Monthly Calculations They will have <b style='color:#e74c3c;'>saved from</b> in sources_notes. and <b style='color:#5dade2;'>Deposit</b> as transaction type.</li>   
  <li>If the extra money coming in from other sources  <b style='color:#e74c3c;'>(not earning)</b>, such as Parents Support, Just record it as  <b style='color:#5dade2;'>Deposit</b> in trnasaction directly.</li>
  <li>If expense from savings, such as Travel Funds or Medium-term Saving, Just record it as  <b style='color:#5dade2;'>Withdraw</b> in trnasaction directly.</li>
  <li>Record <b style='color:#5dade2;'>Transfer Between Accounts</b> after each Monthly Calculations to match the amount in different accounts.</li>   
  
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
    <li><a href="/Monthly_Calculation" style='color: #2980b9;'>Calculate Monthly Expenses and Savings</a> - Summary of your monthly expenses and savings.</li>
    <li><a href="/Funds_Transaction" style='color: #2980b9;'>Make a Transaction</a> - Money move in and out is based on <b style='color:#e74c3c;'>fund category, not actual account</b>.</li>
    <li><a href="/Historical_Stats" style='color: #2980b9;'>View Historical Statistics</a> - Analyze your financial data over time.</li>
    <li><a href="/Traveling_Spending_Stats" style='color: #2980b9;'>View Traveling Spending Statistics</a> - Analyze your travel-related expenses.</li>
    <li><a href="/Current_Saving_Status" style='color: #2980b9;'>View Current Saving Status</a> - Get an overview of your current savings.</li>
    <li><a href="/Statement_Viewer" style='color: #2980b9;'>View Your Detail Earning, Spending, and Saving</a> - Get a detailed view of your financial activities.</li>

  </ul>
 

 
  """, unsafe_allow_html=True)




if __name__ == "__main__":
  main()