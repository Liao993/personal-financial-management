from extract import extract
from transformed import transformation
from load import load_new_house_data
# Path to the credentials inside the container
CREDS_PATH = "/service/google_creds.json"

def run_house_etl():
    
    raw_data = extract(CREDS_PATH)
    transformed_data = transformation(raw_data)
    new_rows_count = load_new_house_data(transformed_data)

    print(f"Sync successful: {new_rows_count} new records added.")
    if new_rows_count == 0:
        print("Everything was already up to date!")


if __name__ == "__main__":
    run_house_etl()