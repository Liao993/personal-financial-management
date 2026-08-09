import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.upload_pdf.pipeline.display import (  # noqa: E402
    build_statement_review_table,
    validate_statement_review_data,
)


class UploadExpenseReviewTests(unittest.TestCase):
    def test_primary_fund_amount_uses_total_when_no_secondary_split(self):
        data = pd.DataFrame(
            [
                {
                    "date": "2026-08-09",
                    "items": "Flight",
                    "amount": 250.00,
                    "category": "Traveling",
                    "traveling_category": "Flight",
                    "trip": "Toronto-082026",
                    "exclude_from_monthly": True,
                    "target_fund_category": "Traveling Funds",
                    "split_fund_category_1": None,
                    "split_amount_1": 0.00,
                }
            ]
        )

        review = build_statement_review_table(data)

        self.assertEqual(review.loc[0, "primary_fund_amount"], 250.00)
        self.assertEqual(review.loc[0, "secondary_fund_amount"], 0.00)

    def test_primary_and_secondary_amounts_show_split_allocation(self):
        data = pd.DataFrame(
            [
                {
                    "date": "2026-08-09",
                    "items": "Hotel",
                    "amount": 300.00,
                    "category": "Traveling",
                    "traveling_category": "Hotel",
                    "trip": "Toronto-082026",
                    "exclude_from_monthly": True,
                    "target_fund_category": "Traveling Funds",
                    "split_fund_category_1": "Emergency Funds",
                    "split_amount_1": 75.00,
                }
            ]
        )

        review = build_statement_review_table(data)

        self.assertEqual(review.loc[0, "primary_fund_amount"], 225.00)
        self.assertEqual(review.loc[0, "secondary_fund_amount"], 75.00)

    def test_traveling_rows_require_withdrawal_and_primary_fund(self):
        data = pd.DataFrame(
            [
                {
                    "amount": 120.00,
                    "category": "Traveling",
                    "traveling_category": "Food",
                    "exclude_from_monthly": False,
                    "target_fund_category": None,
                    "split_fund_category_1": None,
                    "split_amount_1": 0.00,
                }
            ]
        )

        self.assertFalse(
            validate_statement_review_data(
                edited_df=data,
                single_trip=True,
                trip_input="Toronto-082026",
            )
        )


if __name__ == "__main__":
    unittest.main()
