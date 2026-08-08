import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.ai_semantic.query_builder import build_metric_query
from modules.ai_semantic.ollama_client import get_ollama_host
from modules.ai_semantic.router import _normalize_date_range
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

    def test_router_rejects_invalid_dates(self):
        with self.assertRaises(ValueError):
            _normalize_date_range({"start_date": "2026/01/01", "end_date": "2026-07-23"})

    def test_router_rejects_reversed_dates(self):
        with self.assertRaises(ValueError):
            _normalize_date_range({"start_date": "2026-08-01", "end_date": "2026-01-01"})

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
