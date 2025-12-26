import os
import gspread
import pandas as pd
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
    print(df_raw)
    """
    # 3. Transform (Renaming columns to match your 8-field Postgres table)
    # Mapping example: Google Sheet -> Postgres
    df_clean = pd.DataFrame()
    df_clean['date'] = pd.to_datetime(df_raw['Date Column Name']) 
    df_clean['items'] = df_raw['Description Column Name']
    df_clean['amount'] = df_raw['Amount Column Name']
    df_clean['category'] = 'House'
    df_clean['traveling_category'] = None
    df_clean['trip'] = None
    df_clean['source_notes'] = "Sync: " + df_raw['Note Column Name'].astype(str)
    
    # 4. Load
    engine = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}")
    df_clean.to_sql('expense', engine, if_exists='append', index=False)
    print("Sync successful")
    """
if __name__ == "__main__":
    run_house_etl()