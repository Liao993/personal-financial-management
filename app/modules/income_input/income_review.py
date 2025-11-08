import streamlit as st # type: ignore
import pandas as pd # type: ignore
def review_income_input(review_data_key):
    reviewed_data = st.session_state.get(review_data_key, {})
    st.subheader("Your Income Input Information:")
    
    # 2. Prepare the data for display in a table format

    income_date = reviewed_data.get('date', '')
    income_amount = f"${reviewed_data.get('amount', 0.00):,.2f}" 
    income_source = reviewed_data.get('source', '')
    income_regular = 'Yes' if reviewed_data.get('regular', False) else 'No'
    income_notes = reviewed_data.get('notes', '')

    # Create a dictionary where keys are the desired column names
    data = {
        "Date": [income_date],
        "Amount": [income_amount],
        "Source": [income_source],
        "Regular": [income_regular],
        "Notes": [income_notes]
    }
    
    # Optional: Convert the list of dicts to a pandas DataFrame for nicer formatting
    df = pd.DataFrame(data)

    # 3. Display the data using st.table
    st.dataframe(df)

    return reviewed_data