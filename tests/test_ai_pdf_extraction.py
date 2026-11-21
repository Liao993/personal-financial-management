import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.upload_pdf.pipeline.ai_extraction import _normalize_transactions  # noqa: E402


class AIPdfExtractionTests(unittest.TestCase):
    def test_normalization_removes_payments_and_applies_store_rules(self):
        result = _normalize_transactions(
            {
                "transactions": [
                    {
                        "date": "2026-11-01",
                        "items": "SUPERSTORE PE",
                        "amount": "45.20",
                        "category": "Not Categorized",
                    },
                    {
                        "date": "2026-11-02",
                        "items": "PAYMENT - THANK YOU",
                        "amount": -100,
                        "category": "Other",
                    },
                ]
            },
            "My New Card",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["category"], "Grocery")
        self.assertEqual(result.iloc[0]["payment_method"], "My New Card")
        self.assertEqual(result.iloc[0]["amount"], 45.20)
        self.assertEqual(str(result.iloc[0]["date"]), "2026-11-01")


if __name__ == "__main__":
    unittest.main()
