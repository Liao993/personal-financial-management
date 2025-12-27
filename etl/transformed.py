import pandas as pd

def transformation(df_raw):

    df_clean = pd.DataFrame()
    # Formatting Core Data
    df_clean['date'] = pd.to_datetime(df_raw['Date']).dt.date 
    df_clean['items'] = df_raw['Item'].astype(str).str[:255]
    df_clean['amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0).round(2)
    
    # Static Categories
    df_clean['category'] = 'House'
    df_clean['house_category'] = df_raw['Category'].astype(str).str[:255]
    
    # Tie-breaker logic (Google Sheet row number ensures unique identity for identical transactions)
    df_clean['source_notes'] = ('House_Row_' + (df_raw.index + 2).astype(str))

    # Initialize empty columns with correct nullable types to match schema
    df_clean['traveling_category'] = pd.Series([None] * len(df_clean), dtype='string')
    df_clean['trip'] = pd.Series([None] * len(df_clean), dtype='string')
    df_clean['amount_for_number_of_travelers'] = pd.Series([None] * len(df_clean), dtype='Int64')
    df_clean['paid_for_number_of_travlerers'] = pd.Series([None] * len(df_clean), dtype='Int64')

    return df_clean