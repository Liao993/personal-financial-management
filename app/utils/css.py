import streamlit as st # type: ignore
import pandas as pd # type: ignore
from pandas.io.formats.style import Styler # type: ignore # Explicitly import Styler
def drop_down_list():
  st.markdown(
    """
    <style>
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: lightcyan !important;
        color: black !important; /* Optional: Change text color */
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"] {
        background-color: white !important; /* Background for each option */
        color: black !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"]:hover {
        background-color: #f0f8ff !important; /* Hover color for options */
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Styling for Total Row and Column ---
def apply_pivot_table_style(df: pd.DataFrame) -> Styler:
    """
    Applies styling to a fund distribution DataFrame to highlight
    the 'Total' row and 'Total' column differently based on specific rules.

    Args:
        df (pd.DataFrame): The DataFrame to style, expected to have a 'Category' column
                           and a 'Total' row/column.

    Returns:
        Styler: The styled DataFrame.
    """

    
    def _apply_cell_style(cell_val, row_idx, col_name):
        styles = []
        apply_text_style = False

        # Identify if the current row is the 'Total' row by checking the 'Category' column
        # and if the current column is the 'Total' column
        is_total_row = (df.loc[row_idx, 'fund_category'] == 'Total') # Check the 'Category' column value for this row
        is_total_col = (col_name == 'Total')
        
        # Identify the grand total cell and the 'Total' label in the 'Category' column
        is_grand_total_cell = is_total_row and is_total_col
        is_category_total_label = is_total_row and (col_name == 'fund_category') # This will be the 'Total' text in the 'Category' column

        if is_grand_total_cell or is_category_total_label:
            # Leave these cells blank (no background color)
            styles.append('background-color: #00ab41')
            apply_text_style = True
        elif is_total_row: # This is the total row, excluding the grand total cell
            styles.append('background-color: #f1c40f')
            apply_text_style = True
        elif is_total_col: # This is the total column, excluding the grand total cell
            styles.append('background-color: #5dade2') 
            apply_text_style = True
    

        if apply_text_style:
            styles.append('color: black')
            styles.append('font-weight: bold')
            styles.append('font-size: 1000.6em') # Larger font size for emphasis

        return '; '.join(styles)

    # Apply the styling function cell by cell
    styled_df = df.style.apply(lambda x: [
        _apply_cell_style(x[col], x.name, col) # x.name will now be the numerical index
        for col in df.columns
    ], axis=1)


  
    return styled_df
