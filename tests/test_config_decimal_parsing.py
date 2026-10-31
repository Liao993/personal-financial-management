import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from utils.data import _decimal_from_raw  # noqa: E402


class ConfigDecimalParsingTests(unittest.TestCase):
    def test_decimal_expression_resolves_env_references(self):
        with patch.dict(os.environ, {"TFSA_2025": "32500", "TFSA_2026": "7000"}):
            self.assertEqual(_decimal_from_raw("TFSA_2025+TFSA_2026"), Decimal("39500"))

    def test_decimal_parser_tolerates_display_formatting(self):
        self.assertEqual(_decimal_from_raw("$1,234.56"), Decimal("1234.56"))

    def test_invalid_decimal_value_falls_back_to_zero(self):
        self.assertEqual(_decimal_from_raw("not-a-number"), Decimal("0"))


if __name__ == "__main__":
    unittest.main()
