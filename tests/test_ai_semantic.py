import os
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.ai_semantic.query_builder import build_metric_query
from modules.ai_semantic.ollama_client import get_ollama_host
from modules.ai_semantic.router import _format_metric_answer, _normalize_date_range, answer_question
from modules.ai_semantic.semantic_loader import load_semantic_layer


class SemanticLayerTests(unittest.TestCase):
    def test_loader_replaces_dbt_schema_placeholder(self):
        previous = os.environ.get("DBT_SCHEMA")
        os.environ["DBT_SCHEMA"] = "dbt_budget_dev"
        try:
            metrics = load_semantic_layer(ROOT / "dbt" / "budget_project" / "semantic_layer.yml")
        finally:
            if previous is None:
                os.environ.pop("DBT_SCHEMA", None)
            else:
                os.environ["DBT_SCHEMA"] = previous

        self.assertEqual(
            metrics["grocery_spend"]["table"],
            "dbt_budget_dev.intermediate_expenses_with_summary",
        )

    def test_query_builder_parameterizes_dates_and_keeps_filters(self):
        metric = {
            "table": "transactions",
            "date_column": "date",
            "aggregation": "SUM(amount)",
            "filters": ["fund_category = 'Retirement Saving'"],
        }

        sql, params = build_metric_query(metric, "2026-01-01", "2026-07-23")

        self.assertIn("fund_category = 'Retirement Saving'", sql)
        self.assertIn("date BETWEEN %s AND %s", sql)
        self.assertEqual(params, ("2026-01-01", "2026-07-23"))

    def test_query_builder_supports_record_metrics(self):
        metric = {
            "type": "records",
            "table": "transactions",
            "date_column": "date",
            "columns": ["transaction_id", "date", "amount"],
            "filters": ["fund_category = 'Parents Support'", "transaction_type = 'Withdrawal'"],
            "order_by": "date DESC, transaction_id DESC",
            "limit": 100,
        }

        sql, params = build_metric_query(metric, "2026-01-01", "2026-09-17")

        self.assertIn("SELECT transaction_id, date, amount", sql)
        self.assertIn("fund_category = 'Parents Support'", sql)
        self.assertIn("transaction_type = 'Withdrawal'", sql)
        self.assertIn("ORDER BY date DESC, transaction_id DESC", sql)
        self.assertIn("LIMIT 100", sql)
        self.assertEqual(params, ("2026-01-01", "2026-09-17"))

    def test_query_builder_supports_grouped_metrics(self):
        metric = {
            "table": "dbt_budget_dev.intermediate_expenses_with_summary",
            "date_column": "date",
            "aggregation": "SUM(amount)",
            "filters": [],
            "allowed_dimensions": ["category", "month"],
        }

        sql, params = build_metric_query(
            metric,
            "2026-07-01",
            "2026-07-31",
            dimensions=["category", "month"],
        )

        self.assertIn("category AS category", sql)
        self.assertIn("DATE_TRUNC('month', date)::date AS month", sql)
        self.assertIn("SUM(amount) AS value", sql)
        self.assertIn("GROUP BY category, DATE_TRUNC('month', date)::date", sql)
        self.assertIn("ORDER BY value DESC", sql)
        self.assertEqual(params, ("2026-07-01", "2026-07-31"))

    def test_query_builder_rejects_unsupported_grouped_dimension(self):
        metric = {
            "table": "transactions",
            "date_column": "date",
            "aggregation": "SUM(amount)",
            "filters": [],
            "allowed_dimensions": ["fund_category"],
        }

        with self.assertRaises(ValueError):
            build_metric_query(metric, "2026-01-01", "2026-12-31", dimensions=["source_notes"])

    def test_semantic_layer_includes_parent_support_records(self):
        metrics = load_semantic_layer(ROOT / "dbt" / "budget_project" / "semantic_layer.yml")

        self.assertEqual(metrics["parent_support_withdrawals"]["type"], "records")
        self.assertIn("transaction_id", metrics["parent_support_withdrawals"]["columns"])
        self.assertIsNone(metrics["parent_support_balance"]["date_column"])
        self.assertIn("category", metrics["total_expense"]["allowed_dimensions"])
        self.assertIn("fund_category", metrics["total_transaction_amount"]["allowed_dimensions"])

    def test_router_rejects_invalid_dates(self):
        with self.assertRaises(ValueError):
            _normalize_date_range({"start_date": "2026/01/01", "end_date": "2026-07-23"})

    def test_router_rejects_reversed_dates(self):
        with self.assertRaises(ValueError):
            _normalize_date_range({"start_date": "2026-08-01", "end_date": "2026-01-01"})

    def test_parent_support_withdraw_request_routes_to_records_without_ollama(self):
        rows = [
            {
                "transaction_id": 12,
                "date": "2026-07-01",
                "account_name": "Main Chequing",
                "amount": -125.50,
                "fund_category": "Parents Support",
                "transaction_type": "Withdrawal",
                "source_notes": "support",
                "trip": None,
                "expense_id": None,
            }
        ]

        with mock.patch("modules.ai_semantic.router.ask_ollama") as ask_ollama:
            with mock.patch("modules.ai_semantic.router._run_record_metric", return_value=rows):
                result = answer_question("can you help me find all parent support withdraw")

        ask_ollama.assert_not_called()
        self.assertEqual(result["metric"], "parent_support_withdrawals")
        self.assertEqual(result["rows"], rows)
        self.assertIn("totaling $125.50", result["answer"])

    def test_metric_answer_uses_exact_computed_value(self):
        answer = _format_metric_answer("total_expense", 1092.66, "2026-07-01", "2026-07-31")

        self.assertIn("$1,092.66", answer)
        self.assertNotIn("$10,926.60", answer)

    def test_grouped_spending_request_routes_with_dimension_and_date(self):
        rows = [{"category": "Grocery", "value": 123.45}]

        with mock.patch("modules.ai_semantic.router.ask_ollama") as ask_ollama:
            with mock.patch("modules.ai_semantic.router._run_grouped_metric", return_value=rows):
                result = answer_question("total spending for July 2026 by category")

        ask_ollama.assert_not_called()
        self.assertEqual(result["metric"], "total_expense")
        self.assertEqual(result["dimensions"], ["category"])
        self.assertEqual(result["start_date"], "2026-07-01")
        self.assertEqual(result["end_date"], "2026-07-31")
        self.assertEqual(result["rows"], rows)
        self.assertIn("grouped by category", result["answer"])

    def test_ollama_host_uses_host_gateway_inside_container_env(self):
        previous_app_env = os.environ.get("APP_ENV")
        previous_ollama_host = os.environ.get("OLLAMA_HOST")
        os.environ["APP_ENV"] = "production"
        os.environ["OLLAMA_HOST"] = "http://localhost:11434"
        try:
            self.assertEqual(get_ollama_host(), "http://host.docker.internal:11434")
        finally:
            if previous_app_env is None:
                os.environ.pop("APP_ENV", None)
            else:
                os.environ["APP_ENV"] = previous_app_env

            if previous_ollama_host is None:
                os.environ.pop("OLLAMA_HOST", None)
            else:
                os.environ["OLLAMA_HOST"] = previous_ollama_host


if __name__ == "__main__":
    unittest.main()
