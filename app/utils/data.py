#expense
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
    "LUCKYMOBILE": 'Cell Phone',
    "PHOVIETNAM": 'Food Outside',
    
}
#used for catching daily expense from being in traveling category
daily_expense_in_other_provinces = ["COSTCO", "EASTLINK", "HONGMALL", 'HTSP', 'HOPSPOT', "LUCKY MOBILE", "PHO VIETNAM"]

#used for expense input
common_store_list = ['Not Common Store', 'Tsengdok Monastery', 'Sobeys', 'Leonhard', 'Superstore', 'Amazon.ca', 'Leezen', 'Great Enlightenment', 
                     'Dollarama', 'A&W', 'Shoppers Drug Mart', 'Global Grocery', 'Costco', 
                     'Take Sushi', 'Petro', 'Starbucks', 'Irving', 
                     'Hopspot', 'Mike & Andreea', 'Tim Hortons', 'Panda Mart', 'Eastlink', 'Pho Vietnam Rest', 
                     'Saigon Pho', 'Receiver Coffee', 'Wal-Mart', 'Hong Mall', 'Liquor', 'Cows', 'Alambe', 'Mucho Burrito']


expense_category_options = ["Grocery", "Food Outside", "Household Goods", "Cell Phone", "Gas", "Donation", "Gifts", 
                    "House", "Medicine", "Exercise", "Saved For Love", "Transportation", "Education", "Traveling" , 
                    "Fun/Tickets", "Clothing", "Liquor", "Others", "Car"]

# travel expense
hotel_booking = ["AGODA", "BOOKING", "EXPEDIA", "AIRBNB"]
traveling_category_options = ["Flight", "Hotel", "Public Transportation", "Gift", "Gas/Parking/Tolls", "Food", "Tickets", "Others"]

#transaction
fund_categories = ["Traveling Funds", "Retirement Saving", "Medium-term Saving", "House", "Direct Investing", "Parents Support", "Emergency Funds", "Others"]

account_name_list = ["RBC Chequing", "TD House", "EQ 10D Notice", "EQ 30D Notice", "RBC TFSA", "EQ TFSA", "Questrade TFSA (Travel)", "Questrade TFSA (Retire)", "Questrade TFSA (Medium)", "Moomoo RRSP" ]
cashflow_account_name_list = ["RBC Chequing", "EQ 10D Notice", "EQ 30D Notice"]

transaction_type_list = ["Deposit (between funds or savings)", "Withdrawal (between funds or spending)", "Transfer Between Accounts"]

#cashflow
cashflow_transaction_type_list = ["Deposit (Income)", "Withdrawal (Daily and House Expenses)", "Transfer Between Accounts"]
cashflow_purpose = ["Income", "Interest Earning Before Bookeeping", "House Expense" ,"RBC credit card payment", "PC credit card payment", "Debit Card payment", "eTransfer payment", "Cash payment"]

# the one used for database for both transactions and cashflow
transaction_type_database = ["Deposit", "Withdrawal", "Transfer Out", "Transfer In"]

#Change every year
TFSA_room = 32500
RRSP_room = 14729

years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040]

#Default value for income amount in the form
fixed_income_data = 1787.28 