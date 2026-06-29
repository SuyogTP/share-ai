import unittest

from market_pipeline import enrich_market_records


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


if __name__ == "__main__":
    unittest.main()
