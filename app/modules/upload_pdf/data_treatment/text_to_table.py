import pandas as pd
import re
import streamlit as st # type: ignore
def text_to_table(extracted_data):
    selected_data = []
    if extracted_data:
        for filename, text in extracted_data.items():
            for line in text[1:]:
            
              line = line.strip()
              if not line:
                  continue

              match = None

              # Condition 1 & 2: Date Date Description Amount ...
              match = re.search(r'([A-Z]{3}\d{2})\s([A-Z]{3}\d{2})\s(.+?)\s*(\d+\.\d{2})', line)
              if match:
                  selected_data.append([match.group(1), match.group(2), match.group(3).strip(), match.group(4)])
                  continue

              # Condition 3 & 5: Date Date Description $Amount
              match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\$\s*(\d+\.\d{2})', line)
              if match:
                  selected_data.append([match.group(1).replace(' ', ''), match.group(2).replace(' ', ''), match.group(3).strip(), match.group(4)])
                  continue

              # Condition 4: Date Date Description Amount ...
              match = re.search(r'([A-Z]{3}\s?\d{2})\s([A-Z]{3}\s?\d{2})\s(.+?)\s*(\d+\.\d{2})', line)
              if match:
                  selected_data.append([match.group(1).replace(' ', ''), match.group(2).replace(' ', ''), match.group(3).strip(), match.group(4)])
                  continue

        df = pd.DataFrame(selected_data, columns=["Transaction Date", "Post Date", "Description", "Amount"])     
            
    return df