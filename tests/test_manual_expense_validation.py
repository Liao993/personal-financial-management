import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.expense_input.components.expense_form import validate_manual_expense_review  # noqa: E402


class ManualExpenseValidationTests(unittest.TestCase):
    def test_traveling_expense_requires_trip_and_fund_withdrawal(self):
        expense_data = {
            "amount": 100.00,
            "category": "Traveling",
            "traveling_category": "Food",
            "trip": None,
            "exclude_from_monthly": False,
            "target_fund_category": None,
            "split_fund_category_1": None,
            "split_amount_1": 0.00,
        }

        self.assertFalse(validate_manual_expense_review(expense_data))

    def test_valid_traveling_expense_can_continue_to_review(self):
        expense_data = {
            "amount": 100.00,
            "category": "Traveling",
            "traveling_category": "Food",
            "trip": "Toronto-082026",
            "exclude_from_monthly": True,
            "target_fund_category": "Traveling Funds",
            "split_fund_category_1": None,
            "split_amount_1": 0.00,
        }

        self.assertTrue(validate_manual_expense_review(expense_data))


if __name__ == "__main__":
    unittest.main()
