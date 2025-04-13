common_store_directory = {
    'SOBEYS': 'Grocery',
    "LEONHARD'SCAFE&REST": 'Food Outside',
    'ATLANTICSUPERSTORE': 'Grocery',
    'AMAZON.CA': 'Household Goods',
    'BELL MOBILITY': 'Cell Phone',
    'LEEZEN': 'Grocery',
    'GREATENLIGHTENMENT': 'Donation',
    'DOLLARAMA': 'Household Goods',
    'A&W': 'Food Outside',
    'SHOPPERSDRUGMART': 'Medicine',
    'GLOBALGROCERYSTORE': 'Grocery',
    'TAKESUSHI': 'Food Outside',
    'PETRO-CANADA': 'Gas',
    'IKYUNOODLESLIMITED': 'Food Outside',
    'STARBUCKS': 'Food Outside',
    'IRVING': 'Gas',
    'KATSUSANRESTAURANT': 'Food Outside',
    'BUSPASS': 'Transportation',
    'HTSP-*TRANSIT': 'Transportation',
    'MIKE&ANDREEA': 'Grocery',
    'TIMHORTONS': 'Food Outside',
    'PANDAMART': 'Grocery',
    'EASTLINK': 'Cell Phone',
    'PHOVIETNAMREST': 'Food Outside',
    'SPICEYCHEFREST': 'Food Outside',
    'SAIGONPHOVIETNAMESE': 'Food Outside',
    'IMMIGRATIONCANADA': 'Others',
    'RECEIVERCOFFEE': 'Food Outside',
    'WAL-MART': 'Grocery'
}

def categorize_description_with_common_stores(description, common_store_directory):
    description_upper = description.upper()
    for store_name, category in common_store_directory.items():
        if store_name.upper() in description_upper:
            return category
    return None

def categorize_description_travel(description):
    description_parts = description.split()
    if len(description_parts) >= 2:
        last_two_words = " ".join(description_parts[-2:]).upper()
        if not "PE" in last_two_words and not description.upper().startswith("EASTLINK"):
            return "Traveling"
    return None

def categorize_transaction(description, common_store_directory):
    # Check against common store names
    category_by_store = categorize_description_with_common_stores(description, common_store_directory)
    if category_by_store:
        return category_by_store

    # Check for traveling category
    category_by_travel = categorize_description_travel(description)
    if category_by_travel:
        return category_by_travel

    return "Others" # Default category if no match

# Example Usage:
descriptions_to_check = [
    "ATLANTICSUPERSTORECHCHARLOTTETOWNPE",
    "A&W8231STRATFORDPE",
    "GREATENLIGHTENMENTBUMURRAYRIVERPE",
    "KATSUSANRESTAURANTRICHMONDBC",
    "EASTLINK SOMETHING ELSE",
    "RANDOM PLACE IN PE",
    "WAL-MART CANADA",
    "TIM HORTONS",
    "SQ*RECEIVERCOFFEE HALIFAX NS",
    "IMMIGRATIONCANADA OTTAWA ON"
]

for desc in descriptions_to_check:
    category = categorize_transaction(desc, common_store_directory)
    print(f"Description: {desc}, Category: {category}")