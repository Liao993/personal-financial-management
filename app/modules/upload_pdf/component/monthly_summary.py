import pandas as pd
import streamlit as st # type: ignore
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
    st.table(monthly_summary.groupby('month')['amount'].sum().round(2))