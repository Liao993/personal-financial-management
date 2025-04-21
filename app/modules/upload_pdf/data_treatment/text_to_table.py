import pandas as pd
import re
import streamlit as st # type: ignore

def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
             # Skip the header lines
            for line in text[1:]:
               
                # Skip the Payment lines
                if "PAYMENT" not  in line:

                    line = line.strip() #Removes any leading or trailing whitespace 
                    if not line:
                        continue

                    match = None
                    #st.info(line)
                     # Condition : Transaction Date Post Date Description Amount (JANO1 JAN02 cookie 1.00 or -$1.70)
                    # Condition 1: Date Date Description $Amount (Handles optional - before $)
                    match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\s*-\s*\$\s*(\d+\.\d{1,2})', line)
                    if match:
                        selected_data.append([match.group(1).replace(' ', ''), match.group(2).replace(' ', ''), match.group(3).replace('$', '').strip(), "-" + match.group(4)])
                        continue

                    match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\$\s*(\d+\.\d{1,2})', line)
                    if match:
                        selected_data.append([match.group(1).replace(' ', ''), match.group(2).replace(' ', ''), match.group(3).replace('$', '').strip(), match.group(4)])
                        continue

                    # Condition 2: Date Date Description Amount (Handles optional - before amount)
                    match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\s*([+-]?\d+\.\d{1,2})', line)
                    if match:
                        selected_data.append([match.group(1).replace(' ', ''), match.group(2).replace(' ', ''), match.group(3).replace('$', '').strip(), match.group(4)])
                        continue

        df = pd.DataFrame(selected_data, columns=["Transaction Date", "Post Date", "Description", "Amount"])     
            
    return df