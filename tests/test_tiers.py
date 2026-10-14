"""v0.3.0 three-tier relativity tests: consumer channels, perks shelf,
and the relativity report contract."""

import json
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_map():
    with open(os.path.join(REPO, "data", "vendor_map.json")) as f:
        return json.load(f)


def load_perk_categories():
    with open(os.path.join(REPO, "data", "perk_categories.json")) as f:
        return json.load(f)["categories"]


class TestConsumerChannels(unittest.TestCase):
    def test_every_mapped_vendor_has_consumer_channels_key(self):
        d = load_map()
        for m in d["mappings"]:
            if m["status"] == "mapped":
                self.assertIn("consumer_channels", m,
                              "mapped vendor %s missing consumer_channels"
                              % m["ticker"])
                self.assertIsInstance(m["consumer_channels"], list,
                                      "consumer_channels not a list for %s"
                                      % m["ticker"])

    def test_consumer_channels_are_nonempty_strings(self):
        d = load_map()
        for m in d["mappings"]:
            for ch in m.get("consumer_channels", []):
                self.assertIsInstance(ch, str)
                self.assertTrue(ch.strip(), "empty channel for %s"
                                % m["ticker"])

    def test_some_mapped_vendors_honestly_have_none(self):
        d = load_map()
        empty = [m["ticker"] for m in d["mappings"]
                 if m["status"] == "mapped" and not m["consumer_channels"]]
        self.assertTrue(empty, "expected some pure-B2B vendors with []")
        self.assertIn("ACN", empty)  # Accenture: B2B only


class TestPerksShelf(unittest.TestCase):
    def test_every_indirect_vendor_has_perk_assignment(self):
        d = load_map()
        for m in d["mappings"]:
            if m["status"] == "indirect":
                assigns = m.get("perk_assignments", [])
                self.assertTrue(assigns,
                                "indirect vendor %s has no perk assignment"
                                % m["ticker"])

    def test_perk_assignments_reference_valid_categories(self):
        valid = {c["id"] for c in load_perk_categories()}
        d = load_map()
        for m in d["mappings"]:
            for a in m.get("perk_assignments", []):
                self.assertIn(a["perk_category"], valid,
                              "%s references unknown perk category %s"
                              % (m["ticker"], a["perk_category"]))
                self.assertTrue(a["perk"].strip())

    def test_twelve_perk_categories(self):
        self.assertEqual(len(load_perk_categories()), 12)

    def test_all_perk_categories_have_vendors(self):
        d = load_map()
        covered = set()
        for m in d["mappings"]:
            for a in m.get("perk_assignments", []):
                covered.add(a["perk_category"])
        valid = {c["id"] for c in load_perk_categories()}
        self.assertEqual(covered, valid,
                         "uncovered perk categories: %s" % (valid - covered))


class TestRelativityCounts(unittest.TestCase):
    def test_counts_sum_to_500_and_match_stored_coverage(self):
        d = load_map()
        by_status = {}
        for m in d["mappings"]:
            by_status[m["status"]] = by_status.get(m["status"], 0) + 1
        self.assertEqual(sum(by_status.values()), 500)
        self.assertEqual(by_status["mapped"], d["coverage"]["mapped"])
        self.assertEqual(by_status["indirect"], d["coverage"]["indirect"])
        self.assertEqual(by_status["unmapped"], d["coverage"]["unmapped"])
        self.assertEqual(d["coverage"]["total"], 500)
        self.assertEqual(by_status["mapped"], 278)
        self.assertEqual(by_status["indirect"], 32)
        self.assertEqual(by_status["unmapped"], 190)

    def test_relativity_report_structure(self):
        import sys
        sys.path.insert(0, REPO)
        import stack_builder
        d = load_map()
        mappings = d["mappings"]
        perk_cats = load_perk_categories()
        rep = stack_builder.relativity_report(mappings, perk_cats)
        self.assertEqual(rep["total_companies"], 500)
        self.assertEqual(len(rep["tiers"]), 3)
        total = 0
        for t in rep["tiers"]:
            total += t["companies"]
            self.assertEqual(len(t["examples"]), 5)
            self.assertIn("meaning", t)
            self.assertTrue(t["meaning"].strip())
        self.assertEqual(total, 500)
        tier1 = rep["tiers"][0]
        self.assertEqual(tier1["status"], "mapped")
        self.assertGreater(tier1["routable_annual_spend_usd"], 0)
        tier3 = rep["tiers"][2]
        self.assertEqual(tier3["routable_annual_spend_usd"], 0)

    def test_perks_shelf_covers_all_twelve_categories(self):
        import sys
        sys.path.insert(0, REPO)
        import stack_builder
        d = load_map()
        perks = stack_builder.build_perks(d["mappings"],
                                          load_perk_categories(), "smb")
        self.assertEqual(perks["perk_categories_covered"], 12)
        self.assertGreater(perks["estimated_perks_annual_spend_usd"], 0)
        self.assertEqual(perks["perks_vendors_used"], 32)


if __name__ == "__main__":
    unittest.main()
