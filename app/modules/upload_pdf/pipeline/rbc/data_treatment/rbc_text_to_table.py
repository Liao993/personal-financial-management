import pandas as pd
import re
import streamlit as st # type: ignore
from modules.upload_pdf.pipeline.common import exclude_payment_credits, infer_statement_year

def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
            #st.info(text)
            year = infer_statement_year(text, filename)

             # Skip the header lines
            for line in text:
                #st.info(line)
                if "STATEMENT" in line.upper() and re.search(r"\b20\d{2}\b", line):
                    continue
                # Skip the Payment lines
                if "PAYMENT - THANK YOU" not  in line:

                    line = line.strip() #Removes any leading or trailing whitespace 
                    if not line:
                        continue

                    match = None

                    # ... inside your loop ...

                    # Condition 1: Negative amount with $ (e.g., -$1,930.21)
                    # FIX: Changed (\d+\.\d{1,2}) to ([\d,]+\.\d{1,2}) used to catch the comma used for thousands
                    match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\s*-\s*\$\s*([\d,]+\.\d{1,2})', line)
                    if match:
                        # STRATEGY: Remove the comma in the append step using .replace(',', '')
                        amount = "-" + match.group(4).replace(',', '')
                        selected_data.append([
                            match.group(1).replace(' ', ''), 
                            match.group(2).replace(' ', ''), 
                            match.group(3).replace('$', '').strip(), 
                            amount, 
                            year
                        ])
                        continue

                    # Condition 2: Positive amount with $ (e.g., $1,930.21)
                    # FIX: Changed (\d+\.\d{1,2}) to ([\d,]+\.\d{1,2})used to catch the comma used for thousands
                    match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\$\s*([\d,]+\.\d{1,2})', line)
                    if match:
                        # STRATEGY: Remove the comma in the append step
                        amount = match.group(4).replace(',', '')
                        selected_data.append([
                            match.group(1).replace(' ', ''), 
                            match.group(2).replace(' ', ''), 
                            match.group(3).replace('$', '').strip(), 
                            amount, 
                            year
                        ])
                        continue

                    # Condition 3: No $ symbol (e.g., 1,930.21 or -1,930.21)
                    # FIX: Changed ([+-]?\d+\.\d{1,2}) to ([+-]?[\d,]+\.\d{1,2}) used to catch the comma used for thousands
                    match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\s*([+-]?[\d,]+\.\d{1,2})', line)
                    if match:
                        # STRATEGY: Remove the comma in the append step
                        amount = match.group(4).replace(',', '')
                        selected_data.append([
                            match.group(1).replace(' ', ''), 
                            match.group(2).replace(' ', ''), 
                            match.group(3).replace('$', '').strip(), 
                            amount, 
                            year
                        ])
                        continue

        df = pd.DataFrame(selected_data, columns=["date", "Post Date", "items", "amount", "year"])  

        df = df.drop(columns=["Post Date"], errors='ignore') 
        df = exclude_payment_credits(df)
            
    return df
