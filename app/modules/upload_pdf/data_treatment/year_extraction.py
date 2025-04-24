import re

def extract_year_from_statement(text):

    pattern = r"STATEMENT.*?(\d{4})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None