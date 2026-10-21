import streamlit as st # type: ignore
import re
import pandas as pd
from modules.upload_pdf.pipeline.common import exclude_payment_credits, infer_statement_year

def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
            year = infer_statement_year(text, filename)

            for line in text:
                if "STATEMENT" in line.upper() and re.search(r"\b20\d{2}\b", line):
                    continue
                pattern = r"""
                    ^\d+\s+                      # Start of line, transaction number (005), and one or more spaces
                    (?P<date>[A-Za-z]{3}\s\d{1,2})\s+  # CAPTURE 1: Month abbreviation (Nov) and Day (14)
                    (?P<post_date>[A-Za-z]{3}\s\d{1,2})\s+ # CAPTURE 2: Post Date (Nov 16)
                    (?P<items>.*?)\s+            # CAPTURE 3: Non-greedy match for Items (SOBEYS #621... PE)
                    (?P<amount>\d+\.\d{2})$      # CAPTURE 4: Amount (50.00) at the end of the line
                """

                # Use re.search and re.VERBOSE flag for readable pattern
                match = re.search(pattern, line, re.VERBOSE)

                if match:
                    # Extract data using the named capture groups
                    date = match.group('date')
                    post_date = match.group('post_date')
                    items = match.group('items')
                    amount = match.group('amount')
                    year = year
                    # Append the extracted data to your list
                    selected_data.append([date, post_date, items, amount, year])
                        #get the year from the first item
        # Create a DataFrame
        df = pd.DataFrame(selected_data, columns=["date", "Post Date", "items", "amount", "year"])

        df = df.drop(columns=["Post Date"], errors='ignore') 
        df = exclude_payment_credits(df)
        return df
        
