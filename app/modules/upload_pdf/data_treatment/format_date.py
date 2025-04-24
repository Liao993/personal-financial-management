import pandas as pd
import streamlit as st  # type: ignore


def format_transaction_date(df, date_column, date_format='%b%d'):
 

    if date_column not in df.columns:
        st.warning(f"Date column '{date_column}' not found in DataFrame.")
        return df

    if "Year" not in df.columns:
        st.warning(
            "Column 'Year' not found in DataFrame.  Cannot format dates without year."
        )
        return df

    try:
        # Combine the date string with the year
        df[date_column + '_with_year'] = df[date_column].astype(str) + ',' + df["Year"].astype(str)
        # Create a format string that includes the year
        full_date_format = f'{date_format},%Y'
        df[date_column] = pd.to_datetime(
            df[date_column + '_with_year'], format=full_date_format, errors='coerce'
        ).dt.strftime('%Y-%m-%d') 
        df = df.drop(columns=["Year"])  # Remove the Year column if not needed
        df = df.drop(columns=[date_column + '_with_year'])  # Remove the temporary column
    except ValueError:
        st.warning(
            f"Could not automatically convert all values in '{date_column}' to dates using 'Year' column and format '{full_date_format}'. Please edit manually."
        )
    return df