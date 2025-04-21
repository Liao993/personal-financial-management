from utils.data import daily_expense_in_other_provinces, hotel_booking

def categorize_description_travel(description):
    
    current_province = "PE"
   
    last_two_words = description[-2:]
    if not current_province in last_two_words and not any(word in description.upper() for word in daily_expense_in_other_provinces):
        return "Traveling"
    if any(word in description.upper() for word in hotel_booking):
        return "Treveling"
    else:
        return None
