import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from backend import income_backend  # noqa: E402


class IncomeSchemaCompatibilityTests(unittest.TestCase):
    def _connection_without_deposit_account(self):
        cursor = Mock()
        cursor.fetchall.side_effect = [[], [("2026-10-20", 100.0, "Salary", None, None)]]
        cursor.description = [
            ("date",),
            ("amount",),
            ("source",),
            ("notes",),
            ("deposit_account",),
        ]
        connection = Mock()
        connection.cursor.return_value = cursor
        return connection, cursor

    def test_last_income_data_works_before_migration(self):
        connection, cursor = self._connection_without_deposit_account()

        with patch.object(income_backend, "get_db_connection", return_value=connection):
            result = income_backend.fetch_last_income_data()

        self.assertEqual(list(result.columns), [
            "date", "amount", "source", "notes", "deposit_account"
        ])
        self.assertEqual(result.iloc[0]["deposit_account"], None)
        last_query = cursor.execute.call_args_list[-1].args[0]
        self.assertIn("NULL::varchar AS deposit_account", last_query)

    def test_monthly_income_falls_back_to_all_income_before_migration(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = (250.0,)
        connection = Mock()
        connection.cursor.return_value = cursor

        with patch.object(income_backend, "get_db_connection", return_value=connection):
            result = income_backend.fetch_monthly_income(2026, 10)

        self.assertEqual(result, 250.0)
        monthly_query = cursor.execute.call_args_list[-1].args[0]
        self.assertNotIn("deposit_account", monthly_query)


if __name__ == "__main__":
    unittest.main()
