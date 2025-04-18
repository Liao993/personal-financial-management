import streamlit as st # type: ignore
import pandas as pd

from modules.upload_pdf.data_treatment.text_to_table import text_to_table
from modules.upload_pdf.data_treatment.common_category import categorize_description_with_common_stores
from modules.upload_pdf.data_treatment.travel_category import categorize_description_travel

from utils.data import common_store_directory, hotel_booking

def categorize_items(df, common_store_directory):
    
    categories = []
    traveling_categories = []
    for description in df['Description']:
        category = categorize_description_travel(description)
        if category:
            if category == "Traveling":
                traveling_sub_category = "Food"  # Default to Food
                description_upper = description.upper()
                if any(hotel_word in description_upper for hotel_word in hotel_booking):
                    traveling_sub_category = "Hotel"
                categories.append(category)
                traveling_categories.append(traveling_sub_category)
        else:
            category = categorize_description_with_common_stores(description, common_store_directory)
            if category:
                categories.append(category)
                traveling_categories.append(None)
            else:
                categories.append("Not Categorized")  # Or any other default value
                traveling_categories.append(None)
    df['Category'] = categories
    df['Traveling_Category'] = traveling_categories
    return df

def rbc_transformed(extracted_data):
    # Convert the extracted data into a table format
    extracted_df = text_to_table(extracted_data)
    categorized_df = categorize_items(extracted_df, common_store_directory)
    #model = load_transformer()

    #category_options = ["Grocery", "Food Outside", "Household Goods", "Cell Phone", "Gas", "Donation", "Gifts", "Home Deposit", "Medicine", "Saved for Love", "Transportation", "Education", "Traveling" , "Fun / Tickets", "Clothing", "Liquar", "Others"]
    #df['Category'] = df['Description'].apply(lambda x: categorize_description(x, model, category_options))

    return categorized_df
