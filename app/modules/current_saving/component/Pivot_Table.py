import streamlit as st # type: ignore
import pandas as pd
from utils.data import fund_categories, account_name_list
from utils.css import apply_pivot_table_style

def Pivot_Table(data):

    pivot_df = pd.pivot_table(
                data,
                values='amount',
                index='fund_category',
                columns='account_name',
                aggfunc='sum',
                fill_value=0 # Replace NaN with 0 for accounts/categories without transactions
                )
    # Include All category
    pivot_df = pivot_df.reindex(fund_categories, fill_value=0)
    #   Include All account
    pivot_df = pivot_df.reindex(columns=account_name_list, fill_value=0)
     # --- Add Totals ---
    # Add a 'Total' column for each category (row sum)
    pivot_df['Total'] = pivot_df.sum(axis=1)

    # Add a 'Total' row for each account (column sum)
    pivot_df.loc['Total'] = pivot_df.sum(axis=0)

    pivot_df = pivot_df.reset_index()
   
    


    # --- Apply Styling for Total Row and Column ---
    styled_df = apply_pivot_table_style(pivot_df)
   
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
