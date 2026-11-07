import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.current_saving.calculations import calculate_yearly_fund_summary  # noqa: E402


class SavingCalculationTests(unittest.TestCase):
    def test_yearly_net_activity_matches_historical_definition(self):
        transactions = pd.DataFrame(
            [
                {"date": "2026-01-01", "fund_category": "Retirement Saving", "transaction_type": "Deposit", "amount": 100.0, "expense_id": None},
                {"date": "2026-02-01", "fund_category": "Retirement Saving", "transaction_type": "Transfer In", "amount": 2565.25, "expense_id": None},
                {"date": "2026-03-01", "fund_category": "Retirement Saving", "transaction_type": "Transfer Out", "amount": -500.0, "expense_id": None},
                {"date": "2026-04-01", "fund_category": "Retirement Saving", "transaction_type": "Withdrawal", "amount": -25.0, "expense_id": 99},
            ]
        )

        summary = calculate_yearly_fund_summary(transactions)

        self.assertEqual(float(summary.loc[summary["Metrics"] == "R - Net Activity", "2026"].iloc[0]), 2165.25)
        self.assertEqual(float(summary.loc[summary["Metrics"] == "R - Transfer In", "2026"].iloc[0]), 2565.25)


if __name__ == "__main__":
    unittest.main()
