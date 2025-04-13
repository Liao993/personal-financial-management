import pandas as pd

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