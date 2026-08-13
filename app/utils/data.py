import os
from decimal import Decimal

years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040]

# Expense
common_store_directory = {
    'SOBEYS': 'Grocery',
    "LEONHARD": 'Food Outside',
    'SUPERSTORE': 'Grocery',
    'AMAZON.CA': 'Household Goods',
    'LEEZEN': 'Grocery',
    'GREATENLIGHTENMENT': 'Donation',
    'DOLLARAMA': 'Household Goods',
    'A&W': 'Food Outside',
    'SHOPPERSDRUGMART': 'Medicine',
    'GLOBALGROCERY': 'Grocery',
    'COSTCO': 'Grocery',
    'TAKESUSHI': 'Food Outside',
    'PETRO': 'Gas',
    'STARBUCKS': 'Food Outside',
    'IRVING': 'Gas',
    'HTSP': 'Transportation',
    'HOPSPOT': 'Transportation',
    'MIKE&ANDREEA': 'Grocery',
    'TIMHORTONS': 'Food Outside',
    'PANDAMART': 'Grocery',
    'EASTLINK': 'Cell Phone',
    'PHOVIETNAMREST': 'Food Outside',
    'SPICEYCHEFREST': 'Food Outside',
    'SAIGONPHO': 'Food Outside',
    'IMMIGRATIONCANADA': 'Others',
    'RECEIVERCOFFEE': 'Food Outside',
    'WAL-MART': 'Grocery',
    'HONGMALL': 'Grocery',
    'LIQUOR' : 'Liquor',
    'COWS': 'Food Outside',
    'ALAMBE': 'Food Outside',
    'MUCHOBURRITO': 'Food Outside',
    'SOYAWAY': 'Food Outside',
    'BBQ': 'Food Outside',
    "DOMINO'S": 'Food Outside',
    'KFC': 'Food Outside',
    'MRSEAFOOD': 'Grocery',
    'CROSSINGBRIDGE': 'Traveling',
    'PROXI': 'Gas',
    "ESSO": 'Gas',
    "Shell": 'Gas',
    "LUCKYMOBILE": 'Cell Phone',
    "PHOVIETNAM": 'Food Outside',
    "Bell": 'Cell Phone',
}

# Used for catching daily expense from being in traveling category
daily_expense_in_other_provinces = ["COSTCO", "EASTLINK", "HONGMALL", 'HTSP', 'HOPSPOT', "LUCKY MOBILE"]

# used for expense input
common_store_list = ['Not Common Store', 'Tsengdok Monastery', 'Bell Canada', 'Sobeys', 'Leonhard', 'Superstore', 'Amazon.ca', 'Leezen', 'Great Enlightenment', 
                     'Dollarama', 'A&W', 'Shoppers Drug Mart', 'Global Grocery', 'Costco', 
                     'Take Sushi', 'Petro', 'Starbucks', 'Irving', 'Shell',
                     'Hopspot', 'Mike & Andreea', 'Tim Hortons', 'Panda Mart', 'Eastlink', 'Pho Vietnam Rest', 
                     'Saigon Pho', 'Receiver Coffee', 'Wal-Mart', 'Hong Mall', 'Liquor', 'Cows', 'Alambe', 'Mucho Burrito']


expense_category_options = ["Grocery", "Food Outside", "Household Goods", "Cell Phone", "Gas", "Donation", "Gifts", 
                     "Medicine", "Exercise", "Saved For Love", "Transportation", "Education", "Traveling" , 
                    "Fun/Tickets", "Clothing", "Liquor", "Others", "Car", "Technology"]

# travel expense
hotel_booking = ["AGODA", "BOOKING", "EXPEDIA", "AIRBNB"]
traveling_category_options = ["Flight", "Hotel", "Public Transportation", "Gift", "Gas/Parking/Tolls", "Food", "Tickets", "Others"]
payment_method = ["PC", "Scotia_Red", "RBC", "Simplii", "eTransfer", "Debit Card", "Cash", "Account Deduction"]

# transaction
_raw_fund_categories = os.environ.get("FUND_CATEGORIES", "")
fund_categories = [a.strip() for a in _raw_fund_categories.split(",") if a.strip()]
transaction_type_list = ["Deposit (between funds or savings)", "Withdrawal (between funds or spending)", "Transfer Between Accounts"]

_raw_accounts = os.environ.get("ACCOUNT_NAMES", "")
account_name_list = [a.strip() for a in _raw_accounts.split(",") if a.strip()]
transaction_type_list = ["Deposit (between funds or savings)", "Withdrawal (between funds or spending)", "Transfer Between Accounts"]

# the one used for database for both transactions and cashflow
transaction_type_database = ["Deposit", "Withdrawal", "Transfer Out", "Transfer In"]

# Change every year
def env_decimal(name):
    return Decimal(os.environ.get(name, "").strip() or "0")


TFSA_room = env_decimal("TFSA_LIMIT")
RRSP_room = env_decimal("RRSP_LIMIT")

total_mortgage_loan = env_decimal("MORTGAGE_TOTAL")
total_mortgage_left = env_decimal("MORTGAGE_LEFT")
total_principal_paid = total_mortgage_loan - total_mortgage_left
mortgage_payment_history = {
    year: {
        "principal": env_decimal(f"PRINCIPAL_{year}"),
        "interest": env_decimal(f"INTEREST_{year}"),
    }
    for year in years
    if os.environ.get(f"PRINCIPAL_{year}", "").strip()
    or os.environ.get(f"INTEREST_{year}", "").strip()
}

# Default value for income amount in the form
fixed_income_data = float(os.environ.get("BIWEEKLY_INCOME",  "0"))
