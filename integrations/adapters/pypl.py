"""PayPal (PYPL) adapter: checkout orders, sandbox."""

import os

from ..adapter import Adapter, http_form, http_json


class PayPalAdapter(Adapter):
    ticker = "PYPL"
    vendor = "PayPal"
    category = "payments_processing"
    product = "PayPal Checkout"
    api_name = "PayPal Orders API v2 (sandbox)"
    docs_url = "https://developer.paypal.com/docs/api/orders/v2/"
    env_keys = ("PAYPAL_CLIENT_ID", "PAYPAL_SECRET")

    def capabilities(self):
        return ["create and capture checkout orders",
                "payouts (same API family)"]

    def demo(self):
        return {"action": "create_order",
                "order": {"id": "demo-paypal-order-id",
                          "status": "CREATED",
                          "amount": {"currency_code": "USD",
                                     "value": "1200.00"}},
                "fixture": True}

    def _token(self):
        tok = http_form(
            "POST", "https://api-m.sandbox.paypal.com/v1/oauth2/token",
            {"grant_type": "client_credentials"},
            basic_user=os.environ["PAYPAL_CLIENT_ID"],
            basic_pass=os.environ["PAYPAL_SECRET"])
        return tok["access_token"]

    def live(self):
        token = self._token()
        order = http_json(
            "POST",
            "https://api-m.sandbox.paypal.com/v2/checkout/orders",
            headers={"Authorization": "Bearer " + token},
            body={"intent": "CAPTURE",
                  "purchase_units": [{"amount": {"currency_code": "USD",
                                                "value": "1200.00"},
                                      "description": "Stack demo order"}]})
        return {"action": "create_order", "id": order.get("id"),
                "status": order.get("status")}
