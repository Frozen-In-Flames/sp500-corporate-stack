"""Workflow tests: both cross-vendor workflows run end to end in demo mode."""

import os
import unittest

from integrations import ADAPTERS
from integrations.shelf import run_workflow
from workflows import onboarding, order_to_cash


def scrub_env():
    saved = dict(os.environ)
    for cls in ADAPTERS:
        for key in cls.env_keys:
            os.environ.pop(key, None)
    return saved


class TestWorkflows(unittest.TestCase):
    def setUp(self):
        self._saved = scrub_env()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved)

    def test_onboarding_five_vendors(self):
        t = run_workflow(onboarding.WORKFLOW)
        self.assertEqual(len(t["steps"]), 5)
        self.assertEqual(t["vendors"],
                         ["ADBE", "CRM", "GOOGL", "MSFT", "TWLO"])
        self.assertEqual(t["modes"], ["demo"])
        actions = [s["action"] for s in t["steps"]]
        self.assertIn("provision identity account", actions)
        for step in t["steps"]:
            self.assertEqual(step["mode"], "demo")
            self.assertTrue(step["vendor"])

    def test_order_to_cash_four_vendors(self):
        t = run_workflow(order_to_cash.WORKFLOW)
        self.assertEqual(len(t["steps"]), 4)
        self.assertEqual(t["vendors"], ["CSCO", "FDX", "INTU", "PYPL"])
        self.assertEqual(t["modes"], ["demo"])
        for step in t["steps"]:
            self.assertEqual(step["mode"], "demo")
            self.assertTrue(step["vendor"])

    def test_each_step_names_its_vendor(self):
        t = run_workflow(onboarding.WORKFLOW)
        pairs = [(s["step"], s["ticker"]) for s in t["steps"]]
        self.assertEqual(pairs, [(1, "MSFT"), (2, "GOOGL"), (3, "CRM"),
                                 (4, "TWLO"), (5, "ADBE")])


if __name__ == "__main__":
    unittest.main()
