"""Salesforce (CRM) adapter: CRM records via the REST API."""

import os

from ..adapter import Adapter, http_json


class SalesforceAdapter(Adapter):
    ticker = "CRM"
    vendor = "Salesforce"
    category = "crm"
    product = "Sales Cloud"
    api_name = "Salesforce REST API v60.0"
    docs_url = "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/"
    env_keys = ("SF_INSTANCE_URL", "SF_ACCESS_TOKEN")

    def capabilities(self):
        return ["create and query CRM records (leads, contacts, accounts)",
                "pipeline and opportunity objects"]

    def demo(self):
        return {"action": "create_contact",
                "record": {"Id": "demo-003-contact-id",
                           "LastName": "Reyes",
                           "FirstName": "Ava",
                           "Email": "ava.reyes@example.com"},
                "fixture": True}

    def live(self):
        base = os.environ["SF_INSTANCE_URL"].rstrip("/")
        token = os.environ["SF_ACCESS_TOKEN"]
        created = http_json(
            "POST", base + "/services/data/v60.0/sobjects/Contact/",
            headers={"Authorization": "Bearer " + token},
            body={"LastName": "Reyes", "FirstName": "Ava",
                  "Email": "ava.reyes@example.com"})
        return {"action": "create_contact", "id": created.get("id"),
                "success": created.get("success")}
