"""v0.4.0 tier-3 quantification tests: reason codes, live-data schemas,
tier-sum reconciliation, and cache-fallback labeling. No network access."""

import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import live_data
from stack_builder import tier3_report

VALID_CODES = {"defense_gov", "reit", "pharma", "semis", "commodities",
               "other"}


def load_map():
    with open(os.path.join(REPO, "data", "vendor_map.json")) as f:
        return json.load(f)


def fixture_tier3_data():
    mappings = [
        {"ticker": "LMT", "name": "Lockheed Martin", "status": "unmapped",
         "reason_code": "defense_gov", "note": "x"},
        {"ticker": "CPT", "name": "Camden Property Trust", "status": "unmapped",
         "reason_code": "reit", "note": "x"},
        {"ticker": "PFE", "name": "Pfizer Inc.", "status": "unmapped",
         "reason_code": "pharma", "note": "x"},
    ]
    awards = {
        "source": "test", "label": "test awards label",
        "fiscal_years": [2024, 2025], "pulled_at": "2026-01-01T00:00:00+00:00",
        "companies": {
            "LMT": {"name": "Lockheed Martin",
                    "by_year": {"2024": 100.0, "2025": 200.0},
                    "matched_names": ["LOCKHEED MARTIN CORPORATION"],
                    "match_method": "recipient-name token match"},
            "CPT": {"name": "Camden Property Trust",
                    "by_year": {"2024": 0.0, "2025": 0.0},
                    "matched_names": [], "match_method": "x"},
            "PFE": {"name": "Pfizer Inc.",
                    "by_year": {"2024": 5.0, "2025": 7.0},
                    "matched_names": [], "match_method": "x"},
        },
    }
    reits = {
        "source": "test", "label": "test reit label",
        "pulled_at": "2026-01-01T00:00:00+00:00",
        "reits": {
            "CPT": {"name": "Camden Property Trust", "cik": "0000906345",
                    "total_assets_usd": 9000000000.0,
                    "filing_period_end": "2025-12-31", "form": "10-K"},
        },
    }
    return mappings, {"awards": awards, "reits": reits}


class TestReasonCodes(unittest.TestCase):
    def test_every_unmapped_has_valid_reason_code(self):
        d = load_map()
        un = [m for m in d["mappings"] if m.get("status") == "unmapped"]
        self.assertEqual(len(un), 190)
        for m in un:
            self.assertIn(m.get("reason_code"), VALID_CODES,
                          "bad/missing reason_code for %s" % m["ticker"])

    def test_reason_code_counts_sum_to_190(self):
        d = load_map()
        counts = {}
        for m in d["mappings"]:
            if m.get("status") == "unmapped":
                counts[m["reason_code"]] = counts.get(m["reason_code"], 0) + 1
        self.assertEqual(sum(counts.values()), 190)

    def test_defense_and_reit_spot_checks(self):
        d = load_map()
        by_ticker = {m["ticker"]: m for m in d["mappings"]}
        self.assertEqual(by_ticker["LMT"]["reason_code"], "defense_gov")
        self.assertEqual(by_ticker["RTX"]["reason_code"], "defense_gov")
        self.assertEqual(by_ticker["CPT"]["reason_code"], "reit")
        self.assertEqual(by_ticker["WY"]["reason_code"], "reit")
        self.assertEqual(by_ticker["NVDA"]["status"], "mapped")


class TestTier3Report(unittest.TestCase):
    def test_tier_sums_reconcile(self):
        mappings, data = fixture_tier3_data()
        rep = tier3_report(mappings, data, "live")
        self.assertEqual(rep["companies"], 3)
        # 200 (LMT FY2025) + 7 (PFE FY2025) = 207
        self.assertEqual(rep["total_federal_awards_latest_fy_usd"], 207.0)
        self.assertEqual(rep["combined_reit_assets_usd"], 9000000000.0)
        self.assertEqual(rep["latest_fy"], "2025")
        self.assertEqual(set(rep["groups"].keys()),
                         {"defense_gov", "reit", "pharma"})

    def test_live_labeling(self):
        mappings, data = fixture_tier3_data()
        rep = tier3_report(mappings, data, "live")
        self.assertIn("LIVE", rep["source_label"])

    def test_cached_labeling_shows_date(self):
        mappings, data = fixture_tier3_data()
        rep = tier3_report(mappings, data, "cached:2026-01-01T00:00:00+00:00")
        self.assertIn("CACHED", rep["source_label"])
        self.assertIn("2026-01-01", rep["source_label"])

    def test_source_labels_carried(self):
        mappings, data = fixture_tier3_data()
        rep = tier3_report(mappings, data, "live")
        self.assertIn("test awards label", rep["awards_source_label"])
        self.assertIn("test reit label", rep["reit_source_label"])


class TestSchemas(unittest.TestCase):
    def _check_awards_doc(self, doc):
        self.assertIn("label", doc)
        self.assertIn("fiscal_years", doc)
        self.assertIn("pulled_at", doc)
        self.assertIn("companies", doc)
        for t, c in doc["companies"].items():
            self.assertIn("by_year", c)
            self.assertIn("match_method", c)
            for fy, v in c["by_year"].items():
                self.assertTrue(v is None or isinstance(v, (int, float)),
                                "bad award value for %s" % t)

    def _check_reit_doc(self, doc):
        self.assertIn("label", doc)
        self.assertIn("pulled_at", doc)
        self.assertIn("reits", doc)
        for t, r in doc["reits"].items():
            if "error" in r:
                continue
            self.assertIn("total_assets_usd", r)
            self.assertIn("filing_period_end", r)
            self.assertEqual(r.get("form"), "10-K")

    def test_real_cache_files_valid_if_present(self):
        adoc = live_data.load_awards_cache()
        rdoc = live_data.load_reit_cache()
        if adoc is not None:
            self._check_awards_doc(adoc)
        if rdoc is not None:
            self._check_reit_doc(rdoc)
        if adoc is not None and rdoc is not None:
            tickers = {m["ticker"] for m in load_map()["mappings"]
                       if m.get("status") == "unmapped"}
            self.assertEqual(set(adoc["companies"].keys()), tickers)


class TestNameTokens(unittest.TestCase):
    def test_stopwords_stripped(self):
        toks = live_data.distinctive_tokens("Lockheed Martin Corporation")
        self.assertEqual(toks, ["lockheed", "martin"])

    def test_short_name_kept(self):
        toks = live_data.distinctive_tokens("3M Company")
        self.assertIn("3m", toks)

    def test_empty_safe(self):
        self.assertIsInstance(live_data.distinctive_tokens(""), list)


if __name__ == "__main__":
    unittest.main()
