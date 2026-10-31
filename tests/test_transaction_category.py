import sys
import os
from datetime import datetime
from pathlib import Path

import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
os.environ.setdefault("ACCOUNT_NAMES", "Main Chequing,Home Reserve,Notice Savings")
os.environ.setdefault("FUND_CATEGORIES", "Traveling Funds,Retirement Saving,Medium-term Saving,House,Emergency Funds,Others")

from models.transaction_models import Transaction
import models.transaction_models as transaction_models

transaction_models.account_name_list[:] = ["Main Chequing", "Home Reserve", "Notice Savings"]
transaction_models.fund_categories[:] = [
    "Traveling Funds", "Retirement Saving", "Medium-term Saving",
    "House", "Emergency Funds", "Others",
]


def make_transaction(**overrides):
    values = {
        "date": datetime(2026, 1, 1),
        "account_name": "Main Chequing",
        "transaction_type": "Withdrawal",
        "amount": -25,
        "fund_category": "Others",
    }
    values.update(overrides)
    return Transaction(**values)


class TransactionCategoryTests(unittest.TestCase):
    def test_transaction_category_is_preserved(self):
        self.assertEqual(
            make_transaction(transaction_category="Account Balance").transaction_category,
            "Account Balance",
        )


    def test_transaction_category_rejects_unknown_values(self):
        with self.assertRaisesRegex(ValueError, "Transaction category"):
            make_transaction(transaction_category="Travel Withdrawal")


    def test_transaction_category_defaults_for_legacy_callers(self):
        self.assertEqual(make_transaction().transaction_category, "Other")
