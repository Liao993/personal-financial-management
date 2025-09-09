import pandas as pd
import re
import streamlit as st # type: ignore

def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
            for line in text:
                #to extract the year
                if 'Statement date' in line:
                    year_match = re.search(r'\d{4}', line)
                    year = year_match.group() if year_match else None
                    #st.info(year)
                else:
                    #st.info(line)
                   
                    regex_pattern = r"^(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+([\s\S]+?)\s+\$([−+]?\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:[A-Za-z\s]+)?.*$"
                    match = re.search(regex_pattern, line)
                    
                    if match:
                        # The captured groups are:
                        # Group 1: Date (e.g., '12/08')
                        # Group 2: Post Date (e.g., '15/08')
                        # Group 3: Items (e.g., 'ATLANTIC SUPERSTORE CH $')
                        # Group 4: Amount (e.g., '40.00')

                        # Clean up the captured groups
                        date = match.group(1).strip()
                        post_date = match.group(2).strip()
                        items = match.group(3).replace('$', '').strip()  # Remove dollar signs
                        amount = match.group(4).replace('−', '-').replace('+', '').strip() # Clean up +/- signs

                        selected_data.append([date, post_date, items, amount, year])
                            #get the year from the first item
        # Create a DataFrame
        df = pd.DataFrame(selected_data, columns=["date", "Post Date", "items", "amount", "year"])
        df = df.drop(columns=["Post Date"], errors='ignore') 
        return df
           