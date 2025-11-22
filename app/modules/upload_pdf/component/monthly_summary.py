import pandas as pd
import streamlit as st # type: ignore

#Due to the credit card statement across months, I don't know how much I spent in each month.
#The function is used to show the monthly summary
#and seperate traveling category from daily expenses
def monthly_summary(reviewed_data_dict):

    st.write("---")
    st.subheader("Monthly Summary")
   
    review_data_for_summary = {
        'date': reviewed_data_dict.get('date'),
        'amount': reviewed_data_dict.get('amount'),
        'category': reviewed_data_dict.get('category'),
        # Exclude any lists or multi-dimensional data here
    }
    monthly_summary = pd.DataFrame(review_data_for_summary)
    monthly_summary['month'] = pd.to_datetime(monthly_summary['date']).dt.month
    monthly_summary['amount'] = monthly_summary['amount'].astype(float)
    #seperate traveling category from daily expenses
    monthly_summary['travel'] = monthly_summary['category'] == "Traveling"
    #display the monthly summary
    st.table(monthly_summary.groupby(['travel','month'])['amount'].sum().round(2))