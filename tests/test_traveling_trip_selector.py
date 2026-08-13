import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from modules.traveling_stats.middle_layer.select_trip import (  # noqa: E402
    TRIP_PLACEHOLDER,
    build_trip_options,
    get_trip_select_index,
)


class TravelingTripSelectorTests(unittest.TestCase):
    def test_build_trip_options_includes_placeholder_and_filters_blanks(self):
        self.assertEqual(
            build_trip_options(["Toronto-082026", "", None, "Vancouver-012026"]),
            [TRIP_PLACEHOLDER, "Toronto-082026", "Vancouver-012026"],
        )

    def test_missing_saved_trip_uses_placeholder_index(self):
        options = build_trip_options(["Toronto-082026"])

        self.assertEqual(get_trip_select_index(options, "Old-Test-Trip"), 0)


if __name__ == "__main__":
    unittest.main()
