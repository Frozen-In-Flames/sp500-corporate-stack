"""Adapter contract tests: every vendor on the shelf satisfies the interface."""

import csv
import os
import unittest

from integrations import ADAPTERS, Adapter
from integrations.shelf import by_ticker, get_shelf

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scrub_env():
    saved = dict(os.environ)
    for cls in ADAPTERS:
        for key in cls.env_keys:
            os.environ.pop(key, None)
    return saved


class TestAdapterContract(unittest.TestCase):
    def test_every_adapter_is_concrete(self):
        for cls in ADAPTERS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, Adapter))
                inst = cls()
                for attr in ("ticker", "vendor", "category", "product",
                             "api_name", "docs_url"):
                    self.assertTrue(getattr(inst, attr),
                                    "%s.%s is empty" % (cls.__name__, attr))
                self.assertIsInstance(inst.env_keys, tuple)
                self.assertTrue(len(inst.env_keys) > 0)

    def test_capabilities_nonempty(self):
        for cls in ADAPTERS:
            with self.subTest(cls=cls.__name__):
                caps = cls().capabilities()
                self.assertIsInstance(caps, list)
                self.assertTrue(len(caps) > 0)

    def test_demo_mode_green_without_credentials(self):
        saved = scrub_env()
        try:
            for cls in ADAPTERS:
                with self.subTest(cls=cls.__name__):
                    out = cls().run()
                    self.assertEqual(out["mode"], "demo")
                    self.assertEqual(out["ticker"], cls.ticker)
                    self.assertIsInstance(out["result"], dict)
                    self.assertIn("note", out)
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_tickers_are_real_index_members(self):
        with open(os.path.join(REPO, "data", "constituents.csv")) as f:
            tickers = set(r["ticker"] for r in csv.DictReader(f))
        for cls in ADAPTERS:
            with self.subTest(ticker=cls.ticker):
                self.assertIn(cls.ticker, tickers,
                              "%s not in S&P 500 constituents" % cls.ticker)

    def test_tickers_unique(self):
        seen = [c.ticker for c in ADAPTERS]
        self.assertEqual(len(seen), len(set(seen)))

    def test_shelf_lists_all(self):
        shelf = get_shelf()
        self.assertEqual(len(shelf), len(ADAPTERS))
        for entry in shelf:
            self.assertIn("ticker", entry)
            self.assertIn("live_ready", entry)

    def test_by_ticker_unknown(self):
        from integrations import AdapterError
        with self.assertRaises(AdapterError):
            by_ticker("NOPE")


if __name__ == "__main__":
    unittest.main()
