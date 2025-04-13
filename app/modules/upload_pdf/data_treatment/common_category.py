

def categorize_description_with_common_stores(description, common_store_directory):
    description_upper = description.upper()
    for store_name, category in common_store_directory.items():
        if store_name.upper() in description_upper:
            return category
    return None


