import streamlit as st # type: ignore
import pandas as pd # type: ignore
from utils.data import account_name_list

def review_income_input(review_data_key):
    reviewed_data = st.session_state.get(review_data_key, {})
    st.subheader("Your Earning Input Information:")

    income_date         = reviewed_data.get('date', '')
    income_amount       = f"${reviewed_data.get('amount', 0.00):,.2f}"
    income_source       = reviewed_data.get('source', '')
    income_regular      = 'Yes' if reviewed_data.get('regular', False) else 'No'
    income_notes        = reviewed_data.get('notes', '')
    default_account = account_name_list[0] if account_name_list else 'Main Chequing'
    deposit_account     = reviewed_data.get('deposit_account', default_account)
    exclude_from_monthly = 'Yes' if reviewed_data.get('exclude_from_monthly', False) else 'No'
    fund_category = reviewed_data.get('fund_category') or ''

    data = {
        "Date":            [income_date],
        "Amount":          [income_amount],
        "Source":          [income_source],
        "Regular":         [income_regular],
        "Notes":           [income_notes],
        "Deposit Account": [deposit_account],
        "Exclude from Monthly Calculation": [exclude_from_monthly],
        "Fund Category": [fund_category],
    }

    df = pd.DataFrame(data)
    st.dataframe(df)

    return reviewed_data
