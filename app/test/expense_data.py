import pandas as pd

data = [
    {'date': '2024/02/03', 'price': 100, 'category': 'saved for love'},
    {'date': '2024/02/04', 'price': 100, 'category': 'grocery'},
    {'date': '2024/02/05', 'price': 200, 'category': 'food outside'},
    {'date': '2024/02/06', 'price': 200, 'category': 'food outside'},
    {'date': '2024/02/07', 'price': 300, 'category': 'grocery'},
    {'date': '2024/02/08', 'price': 300, 'category': 'mobile'},
    {'date': '2024/02/09', 'price': 300, 'category': 'mobile'},
    {'date': '2024/02/10', 'price': 100, 'category': 'education'},
    {'date': '2024/02/11', 'price': 500, 'category': 'donation'},
    {'date': '2024/02/12', 'price': 600, 'category': 'traveling'},
    {'date': '2024/02/13', 'price': 700, 'category': 'food outside'},
    {'date': '2024/02/14', 'price': 1000, 'category': 'home'},
    {'date': '2024/02/15', 'price': 200, 'category': 'traveling'},
    {'date': '2024/02/16', 'price': 30, 'category': 'gift'},
    {'date': '2024/02/17', 'price': 50, 'category': 'gift'},
    {'date': '2024/02/18', 'price': 20, 'category': 'fun'},
    {'date': '2024/02/19', 'price': 100, 'category': 'transportation'},
    {'date': '2024/02/20', 'price': 100, 'category': 'transportation'},
    {'date': '2024/02/21', 'price': 60, 'category': 'gas'},
    {'date': '2024/02/22', 'price': 40, 'category': 'gas'},
    {'date': '2024/02/23', 'price': 200, 'category': 'liquar'}
]

def create_expense_dataframe():
    """Creates a Pandas DataFrame from a list of dictionaries."""
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    expense_df = create_expense_dataframe()