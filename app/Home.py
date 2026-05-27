import streamlit as st # type: ignore

def main():
  st.set_page_config(page_title="Home", page_icon="💸", layout='wide')

  st.markdown("""
  <p style='font-size: 40px; text-align: center; color: #5dade2;'>Personal Finance Management</p>

  <b style='color:#f1c40f; font-size: 24px;'>Income Rules</b>
  <ul style='font-size: 20px;'>
    <li>Any <b style='color:#e74c3c;'>earning</b>, regular or sudden, should be recorded with <b style='color:#5dade2;'>Income Input</b>, then distributed with Monthly Calculations.</li>
  </ul>

  <hr/>

  <b style='color:#f1c40f; font-size: 24px;'>Expense Rules</b>
  <ul style='font-size: 20px;'>
    <li>If the expense is a <b style='color:#e74c3c;'>monthly daily expense</b>, use <b style='color:#5dade2;'>Manual Expense Input</b> or <b style='color:#5dade2;'>Upload Statement</b>.</li>
    <li>House expenses should be recorded as <b style='color:#5dade2;'>House Deposit in Transaction</b>.</li>
    <li><b style='color:#5dade2;'>Prepaid</b> expenses (e.g. helping a friend pay, expect full repayment within the same bookkeeping period) do <b style='color:#e74c3c;'>NOT</b> need to be recorded. Simply skip them.</li>
    <li>If you paid and are waiting for a <b style='color:#e74c3c;'>refund</b> (e.g. hotel cancellation, returned item, partial credit), record the expense normally first. When the refund arrives, go to <b style='color:#5dade2;'>Page 16 Expense Editor</b> to update the amount or delete the record, then <b style='color:#5dade2;'>Rerun Calculation</b> on Page 6 if it affects that month's saving.</li>
    <li>Expenses marked <b style='color:#5dade2;'>Fund Withdrawal Required</b> are excluded from monthly spending totals and auto-create a withdrawal from the selected fund. Use <b style='color:#5dade2;'>Page 16</b> to edit these if the amount changes.</li>
  </ul>

  <hr/>

  <b style='color:#f1c40f; font-size: 24px;'>Refund & Edit Rules</b>
  <ul style='font-size: 20px;'>
    <li><b style='color:#e74c3c;'>Full refund:</b> Go to Page 16 Expense Editor and <b style='color:#5dade2;'>delete the expense</b>. Linked fund transactions delete automatically. Rerun Calculation on Page 6 if it was a regular expense affecting that month's saving.</li>
    <li><b style='color:#e74c3c;'>Partial refund:</b> Go to Page 16 and <b style='color:#5dade2;'>update the amount</b> to the final amount you actually paid. Add a note like "partial refund applied" in the Notes field. Linked fund transactions update automatically via trigger.</li>
    <li><b style='color:#e74c3c;'>Wrong category or amount entered:</b> Go to Page 16 to correct it. No need to delete and re-enter.</li>
    <li><b style='color:#e74c3c;'>Month saving totals changed after editing:</b> Go to Page 6 Monthly Calculation, select the affected month, and click <b style='color:#5dade2;'>Rerun Calculation</b>. This deletes and recreates only the "saved from" deposit records for that month. Manually added deposits are untouched.</li>
  </ul>

  <hr/>

  <b style='color:#f1c40f; font-size: 24px;'>Transaction Rules</b>
  <ul style='font-size: 20px;'>
    <li>The <b style='color:#e74c3c;'>Monthly Saving and House</b> deposits should be recorded via <b style='color:#5dade2;'>Monthly Calculations</b>. They will have <b style='color:#e74c3c;'>saved from</b> in source_notes and <b style='color:#5dade2;'>Deposit</b> as transaction type.</li>
    <li>If extra money comes in from other sources <b style='color:#e74c3c;'>(not earning)</b>, such as Parents Support, record it as a <b style='color:#5dade2;'>Deposit</b> in Transaction directly.</li>
    <li>If spending from savings (Travel Funds, Medium-term Saving), record it as a <b style='color:#5dade2;'>Withdrawal</b> in Transaction directly. <b style='color:#e74c3c;'>Exception:</b> expenses marked Fund Withdrawal Required on the expense form auto-create this transaction — do not record it manually again.</li>
    <li>Record <b style='color:#5dade2;'>Transfer Between Accounts</b> after each Monthly Calculation to match amounts across different accounts.</li>
  </ul>
  """, unsafe_allow_html=True)

  st.divider()

  st.markdown("""
  <p style='font-size: 24px; color: #5dade2;'>
  Navigate to different sections of the app to manage your finances:
  </p>
  <ul style='font-size: 18px; color: #f1c40f;'>
    <li><a href="/Monthly_Income_Input" style='color: #2980b9;'>Input Monthly Income</a> — Enter your monthly income details.</li>
    <li><a href="/Manual_Expense_Input" style='color: #2980b9;'>Input Single Expense</a> — Input a single expense manually. For prepaid items you expect back soon, skip recording. For paid-and-waiting-for-refund items, record here then edit on Page 16 when refund arrives.</li>
    <li><a href="/Upload_Expense" style='color: #2980b9;'>Upload Your Expense Statement</a> — Upload your bank statement. Same refund rules apply.</li>
    <li><a href="/Monthly_Calculation" style='color: #2980b9;'>Calculate Monthly Expenses and Savings</a> — Summary of monthly expenses and savings. Use Rerun Calculation if expenses changed after saving.</li>
    <li><a href="/Funds_Transaction" style='color: #2980b9;'>Make a Transaction</a> — Money move in and out based on <b style='color:#e74c3c;'>fund category, not actual account</b>. Do not manually record withdrawals for expenses already marked Fund Withdrawal Required.</li>
    <li><a href="/Historical_Stats" style='color: #2980b9;'>View Historical Statistics</a> — Analyse your financial data over time.</li>
    <li><a href="/Traveling_Spending_Stats" style='color: #2980b9;'>View Traveling Spending Statistics</a> — Analyse travel-related expenses.</li>
    <li><a href="/Current_Saving_Status" style='color: #2980b9;'>View Current Saving Status</a> — Overview of your current savings and fund balances.</li>
    <li><a href="/Statement_Viewer" style='color: #2980b9;'>View Your Detail Earning, Spending, and Saving</a> — Detailed view of all financial activities.</li>
    <li><a href="/Expense_Editor" style='color: #2980b9;'>✏️ Expense Editor</a> — Edit amount, change category, or delete expenses. Linked fund transactions update automatically. Use this for all refunds and corrections.</li>
  </ul>
  """, unsafe_allow_html=True)


if __name__ == "__main__":
  main()
