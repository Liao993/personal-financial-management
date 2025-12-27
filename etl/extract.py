import os
import gspread
import numpy as np
import pandas as pd
def extract(filepath):
    gc = gspread.service_account(filename=filepath)
    sh = gc.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    worksheet = sh.worksheet(os.getenv("GOOGLE_SHEET_NAME"))
    
    # 2. Extract & Initial Clean
    df_raw = pd.DataFrame(worksheet.get_all_records())
    # Replace empty strings with NaN and drop rows where Date is missing
    df_raw['Date'] = df_raw['Date'].replace(r'^\s*$', np.nan, regex=True)
    df_raw = df_raw.dropna(subset=['Date'])

    return df_raw