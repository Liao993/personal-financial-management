import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
from modules.upload_pdf.pipeline.pc.data_treatment.pc_text_to_table import text_to_table
from modules.upload_pdf.pipeline.pc.data_treatment.pc_format_date import format_transaction_date

from modules.upload_pdf.middle_layer.common_category import categorize_description_with_common_stores
from modules.upload_pdf.middle_layer.travel_category import categorize_description_travel


from utils.data import common_store_directory, hotel_booking

def categorize_items(df, common_store_directory):
    
    categories = []
    traveling_categories = []
    for description in df['items']:
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
    df['category'] = categories
    df['traveling_category'] = traveling_categories
    df['trip'] = None
    return df

def pc_transformed(extracted_data):
 
    # Convert the extracted data into a table format

    extracted_df = text_to_table(extracted_data)

    
    # Format the transaction date
    date_transformed_df = format_transaction_date(extracted_df, date_column='date')
    date_transformed_df['date'] = pd.to_datetime(date_transformed_df['date']).dt.date

    #Amount data type
    date_transformed_df['amount'] = date_transformed_df['amount'].astype(float).map(lambda x: f"{x:.2f}")

    # Categorize items
    categorized_df = categorize_items(date_transformed_df, common_store_directory)


    return categorized_df
    