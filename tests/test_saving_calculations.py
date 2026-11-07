import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.current_saving.calculations import (  # noqa: E402
    calculate_account_flow_summary,
    calculate_fund_category_summary,
    calculate_yearly_fund_summary,
)


class SavingCalculationTests(unittest.TestCase):
    def test_fund_category_summary_combines_monthly_and_yearly_rows(self):
        transactions = pd.DataFrame(
            [
                {"date": "2026-01-01", "fund_category": "Retirement Saving", "transaction_type": "Deposit", "amount": 100.0},
                {"date": "2026-01-15", "fund_category": "Medium-term Saving", "transaction_type": "Deposit", "amount": 50.0},
                {"date": "2026-01-20", "fund_category": "Traveling Funds", "transaction_type": "Withdrawal", "amount": -10.0},
                {"date": "2026-01-21", "fund_category": "Retirement Saving", "transaction_type": "Transfer In", "amount": 500.0},
            ]
        )

        summary = calculate_fund_category_summary(transactions)

        retirement_month = summary[
            (summary["Year"] == 2026)
            & (summary["Month"] == "January")
            & (summary["Fund Category"] == "Retirement Saving")
        ].iloc[0]
        self.assertEqual(retirement_month["Net Saving"], 100.0)
        self.assertEqual(retirement_month["Annual Net Saving"], 100.0)
        self.assertEqual(retirement_month["Annual Net Saving (Retire+Medium)"], 150.0)
        self.assertEqual(retirement_month["Annual Net Saving (R+M+T)"], 140.0)
        self.assertEqual(retirement_month["Annual Net Saving (All)"], 140.0)

    def test_account_flow_summary_keeps_transfer_columns(self):
        transactions = pd.DataFrame(
            [
                {"date": "2026-01-01", "account_name": "Checking", "transaction_type": "Transfer Out", "amount": -100.0},
                {"date": "2026-01-01", "account_name": "TFSA", "transaction_type": "Transfer In", "amount": 100.0},
            ]
        )

        summary = calculate_account_flow_summary(transactions)
        total = summary[summary["Account"] == "All Accounts"].iloc[0]
        self.assertEqual(total["Transfer In"], 100.0)
        self.assertEqual(total["Transfer Out"], 100.0)
        self.assertEqual(total["Net Account Flow"], 0.0)
        self.assertEqual(total["Yearly Net Account Flow"], 0.0)

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
