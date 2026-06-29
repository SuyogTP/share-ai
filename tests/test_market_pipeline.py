import unittest

from market_pipeline import _sanitize_records, enrich_market_records


class MarketPipelineTests(unittest.TestCase):
    def test_enrich_market_records_adds_trend_and_interpretation(self):
        records = [
            {
                "symbol": "NABIL",
                "name": "Nabil Bank",
                "ltp": 1000,
                "change_pct": 1.2,
                "volume": 10000,
                "eps": 80,
                "pe_ratio": 12.5,
                "book_value": 500,
                "dividend_yield": 8.0,
            }
        ]

        df = enrich_market_records(records)

        self.assertIn("trend_result", df.columns)
        self.assertIn("interpretation", df.columns)
        self.assertGreater(len(df), 0)
        self.assertIsInstance(df.loc[0, "trend_result"], dict)
        self.assertIn("lean", df.loc[0, "interpretation"])

    def test_sanitize_records_drops_invalid_rows(self):
        records = [
            {"symbol": "NABIL", "ltp": 1000, "change_pct": 1.2, "volume": 10000},
            {"symbol": "41", "ltp": 0, "change_pct": 0, "volume": 0},
            {"symbol": "EBL", "ltp": 900, "change_pct": 0.5, "volume": 5000},
        ]
        cleaned = _sanitize_records(records)
        self.assertEqual(len(cleaned), 2)
        self.assertTrue(all(item["symbol"] != "41" for item in cleaned))


if __name__ == "__main__":
    unittest.main()
