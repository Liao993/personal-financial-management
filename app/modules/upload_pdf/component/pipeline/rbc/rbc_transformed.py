import streamlit as st # type: ignore
import pandas as pd
from modules.upload_pdf.component.transformer import load_transformer, categorize_description

def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
            for i in  text[1: ]:
              items_trimed = i.split(" ")
              items_trimed = items_trimed[:4]
              if not items_trimed[1].startswith("$") and not items_trimed[2].startswith("PAYMENT"):
                selected_data.append(items_trimed)

        df = pd.DataFrame(selected_data, columns=["Transaction Date", "Post Date", "Description", "Amount"])     
            
    return df


def rbc_transformed(extracted_data):
    # Convert the extracted data into a table format
    df = text_to_table(extracted_data)
    #model = load_transformer()

    #category_options = ["Grocery", "Food Outside", "Household Goods", "Cell Phone", "Gas", "Donation", "Gifts", "Home Deposit", "Medicine", "Saved for Love", "Transportation", "Education", "Traveling" , "Fun / Tickets", "Clothing", "Liquar", "Others"]
    #df['Category'] = df['Description'].apply(lambda x: categorize_description(x, model, category_options))

    return df
