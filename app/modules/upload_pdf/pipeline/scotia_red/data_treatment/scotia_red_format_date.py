import pandas as pd
import streamlit as st  # type: ignore


def format_transaction_date(df, date_column, date_format='%b%d'):
 

    if date_column not in df.columns:
        st.warning(f"Date column '{date_column}' not found in DataFrame.")
        return df

    if "year" not in df.columns:
        st.warning(
            "Column 'Year' not found in DataFrame.  Cannot format dates without year."
        )
        return df

    try:
      
        # 1. Create a combined date string: "Nov 14 2025"
        df['full_date_str'] = df['date'] + ' ' + df['year'].astype(str)

        # 2. Convert the combined string to a datetime object
        # '%b %d %Y' is the format code for Month Abbreviation (Nov), Day (14), Year (2025)
        df['date'] = pd.to_datetime(df['full_date_str'], format='%b %d %Y')

        # 3. Format the datetime object back into the desired 'YYYY-MM-DD' string format
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
      
        df = df.drop(columns=["year"])  # Remove the Year column if not needed
        df = df.drop(columns=['full_date_str'])  # Remove the temporary column
    except ValueError:
        st.warning(
            f"Could not automatically convert all values in '{date_column}'  Please edit manually."
        )
    return df