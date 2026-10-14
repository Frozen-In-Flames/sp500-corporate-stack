"""Intuit (INTU) adapter: QuickBooks Online sandbox, accounting."""

import os

from ..adapter import Adapter, http_json


class QuickBooksAdapter(Adapter):
    ticker = "INTU"
    vendor = "Intuit"
    category = "accounting"
    product = "QuickBooks Online"
    api_name = "QuickBooks Online Accounting API (sandbox)"
    docs_url = "https://developer.intuit.com/app/developer/qbo/docs/get-started"
    env_keys = ("QBO_ACCESS_TOKEN", "QBO_REALM_ID")

    def capabilities(self):
        return ["create invoices and bills",
                "customer and vendor records",
                "profit-and-loss reports"]

    def demo(self):
        return {"action": "create_invoice",
                "invoice": {"Id": "demo-1042",
                            "CustomerRef": {"value": "1", "name": "Acme Corp"},
                            "TotalAmt": 1200.00,
                            "DueDate": "2026-11-13"},
                "fixture": True}

    def live(self):
        token = os.environ["QBO_ACCESS_TOKEN"]
        realm = os.environ["QBO_REALM_ID"]
        inv = http_json(
            "POST",
            "https://sandbox-quickbooks.api.intuit.com/v3/company/%s/invoice"
            "?minorversion=75" % realm,
            headers={"Authorization": "Bearer " + token},
            body={"CustomerRef": {"value": "1"},
                  "Line": [{"Amount": 1200.00,
                            "DetailType": "SalesItemLineDetail",
                            "SalesItemLineDetail": {
                                "ItemRef": {"value": "1", "name": "Services"}}}],
                  "DueDate": "2026-11-13"})
        inv = inv.get("Invoice", inv)
        return {"action": "create_invoice", "id": inv.get("Id"),
                "total": inv.get("TotalAmt")}
