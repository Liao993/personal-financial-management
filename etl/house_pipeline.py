import os
import gspread
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


# Path to the credentials inside the container
CREDS_PATH = "/service/google_creds.json"

def run_house_etl():
    # 1. Connect using the mounted service folder
    gc = gspread.service_account(filename=CREDS_PATH)
    
    # 2. Extract
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.worksheet(sheet_name)
    df_raw = pd.DataFrame(worksheet.get_all_records())
    #drop empty rows - gspread often interprets "empty" cells as empty strings ("")
    # Use np.nan to make them as None or NaN (Not a Number) values.
    df_raw['Date'] = df_raw['Date'].replace(r'^\s*$', np.nan, regex=True)
    df_raw = df_raw[df_raw['Date'].notnull()]
    print(len(df_raw))
    # 3. Transform (Renaming columns to match your 8-field Postgres table)
    # Mapping example: Google Sheet -> Postgres
    df_clean = pd.DataFrame()
    df_clean['date'] = pd.to_datetime(df_raw['Date']) 
    df_clean['items'] = df_raw['Item']
    #make sure the Amount is Numeric and round to 2 decimal
    df_clean['amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').round(2)
    df_clean['category'] = 'House'
    df_clean['traveling_category'] = None
    df_clean['trip'] = None
    df_clean['source_notes'] = None
    df_clean['amount_for_number_of_travelers'] = None
    df_clean['paid_for_number_of_travlerers'] = None
    df_clean['house_category'] = df_raw['Category']
    print(df_clean)
    
    
    # 4. Load
    engine = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}")
    df_clean.to_sql('expense', engine, if_exists='append', index=False)
    print("Sync successful")
    return (df_clean)
if __name__ == "__main__":
    run_house_etl()