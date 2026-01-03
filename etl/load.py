import os
from sqlalchemy import create_engine, text
from sqlalchemy.types import Integer, Numeric, Date, String

def load_new_house_data(df_clean):
    # 4. Load
    db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    engine = create_engine(db_url)
    
    # A. Push to staging (using explicit types for database safety)
    df_clean.to_sql(
        'stg_house', 
        engine, 
        if_exists='replace', 
        index=False,
        dtype={
            'date': Date,
            'items': String(255),
            'amount': Numeric(10, 2),
            'category': String(255),
            'source_notes': String(255),
            'traveling_category': String(255),
            'trip': String(255),
            'amount_for_number_of_travelers': Integer,
            'paid_for_number_of_travlerers': Integer,
            'house_category': String(255)
        }
    )
    
    # B. Upsert into main table (Matching 4 columns for unique check)
    upsert_sql = """
        INSERT INTO expense (
            date, items, amount, category, traveling_category, 
            trip, source_notes, amount_for_number_of_travelers, 
            paid_for_number_of_travlerers, house_category
        )
        SELECT 
            date, 
            items, 
            amount, 
            category, 
            traveling_category, 
            trip, 
            source_notes, 
            amount_for_number_of_travelers::INTEGER, -- Explicit Cast
            paid_for_number_of_travlerers::INTEGER,   -- Explicit Cast
            house_category
        FROM stg_house
        ON CONFLICT (date, items, amount, source_notes) DO NOTHING;
    """
    
    with engine.begin() as conn:
        #If I want to sync any update in Excel, I need to delete the records first
        # Remove all old 'House' records
        #conn.execute(text("DELETE FROM expense WHERE category = 'House';"))
        result = conn.execute(text(upsert_sql))
        new_rows_count = result.rowcount
        conn.execute(text("DROP TABLE stg_house;"))
    
    return new_rows_count