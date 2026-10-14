"""Visa (V) adapter: Visa Direct push funds transfer, sandbox, mutual TLS."""

import base64
import os

from ..adapter import Adapter, http_json


class VisaAdapter(Adapter):
    ticker = "V"
    vendor = "Visa"
    category = "payments_processing"
    product = "Visa Direct"
    api_name = "Visa Direct Funds Transfer API (sandbox)"
    docs_url = "https://developer.visa.com/capabilities/visa_direct"
    env_keys = ("VISA_USER", "VISA_PASS", "VISA_CERT", "VISA_KEY")

    def capabilities(self):
        return ["push funds to a card (payouts, refunds)",
                "pull funds (collections)"]

    def demo(self):
        return {"action": "push_funds",
                "transfer": {"transactionIdentifier": 987654321012345,
                             "approvalCode": "DEM001",
                             "responseCode": "00",
                             "transmissionDateTime": "2026-10-13T00:00:00.000Z"},
                "fixture": True}

    def live(self):
        user = os.environ["VISA_USER"]
        token = base64.b64encode(
            ("%s:%s" % (user, os.environ["VISA_PASS"])).encode()).decode()
        body = {
            "systemsTraceAuditNumber": "451001",
            "retrievalReferenceNumber": "330000550000",
            "localTransactionDateTime": "2026-10-13T00:00:00",
            "acquiringBin": "408999",
            "acquirerCountryCode": "840",
            "senderAccountNumber": "4111111111111111",
            "senderCountryCode": "840",
            "senderCurrencyCode": "USD",
            "recipientPrimaryAccountNumber": "4957030420210496",
            "recipientName": "Stack Demo",
            "transactionCurrencyCode": "USD",
            "transactionIdentifier": "381228649430015",
            "amount": "1.00",
            "businessApplicationId": "AA",
            "merchantCategoryCode": "6012",
        }
        resp = http_json(
            "POST",
            "https://sandbox.api.visa.com/visadirect/fundstransfer/v1"
            "/pushfundstransactions",
            headers={"Authorization": "Basic " + token},
            body=body,
            client_cert=os.environ["VISA_CERT"],
            client_key=os.environ["VISA_KEY"])
        return {"action": "push_funds",
                "transactionIdentifier": resp.get("transactionIdentifier"),
                "approvalCode": resp.get("approvalCode"),
                "responseCode": resp.get("responseCode")}
