import streamlit as st # type: ignore
import re
import pandas as pd
def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
            if 'e-statement' in filename:
                    year_match = re.search(r'\d{4}\b', filename)
                    year = year_match.group() if year_match else None

            for line in text:
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
        return df
        