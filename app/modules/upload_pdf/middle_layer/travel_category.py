from utils.data import daily_expense_in_other_provinces, hotel_booking

def categorize_description_travel(description):
    
    current_residence = ["PE", "CH"]
    last_two_words = description[-2:]
    if (last_two_words not in current_residence) and not any(word in description.upper() for word in daily_expense_in_other_provinces):
        return "Traveling"
    if any(word in description.upper() for word in hotel_booking):
        return "Treveling"
    else:
        return None
