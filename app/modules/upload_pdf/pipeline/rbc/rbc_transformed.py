import streamlit as st # type: ignore
import pandas as pd

from modules.upload_pdf.data_treatment.text_to_table import text_to_table
from modules.upload_pdf.data_treatment.common_category import categorize_description_travel, categorize_description_with_common_stores


from utils.data import common_store_directory

def categorize_items(df, common_store_directory):
    
    categories = []
    for description in df['Description']:
        category = categorize_description_travel(description)
        if category:
            categories.append(category)
        else:
            category = categorize_description_with_common_stores(description, common_store_directory)
            if category:
                categories.append(category)
            else:
                categories.append("Not Categorized")  # Or any other default value

    df['Category'] = categories
    return df

def rbc_transformed(extracted_data):
    # Convert the extracted data into a table format
    extracted_df = text_to_table(extracted_data)
    categorized_df = categorize_items(extracted_df, common_store_directory)
    #model = load_transformer()

    #category_options = ["Grocery", "Food Outside", "Household Goods", "Cell Phone", "Gas", "Donation", "Gifts", "Home Deposit", "Medicine", "Saved for Love", "Transportation", "Education", "Traveling" , "Fun / Tickets", "Clothing", "Liquar", "Others"]
    #df['Category'] = df['Description'].apply(lambda x: categorize_description(x, model, category_options))

    return categorized_df
