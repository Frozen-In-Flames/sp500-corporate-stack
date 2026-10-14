"""UPS (UPS) adapter: rate quotes via the Rating API."""

import os

from ..adapter import Adapter, http_form, http_json


class UpsAdapter(Adapter):
    ticker = "UPS"
    vendor = "UPS"
    category = "parcel_shipping"
    product = "UPS Developer APIs"
    api_name = "UPS Rating API v1"
    docs_url = "https://developer.ups.com/api/reference?loc=en_US#operation/Rate"
    env_keys = ("UPS_CLIENT_ID", "UPS_CLIENT_SECRET", "UPS_ACCOUNT")

    def capabilities(self):
        return ["rate quotes",
                "shipment creation and tracking (same API family)"]

    def demo(self):
        return {"action": "rate_quote",
                "quote": {"serviceCode": "03",
                          "serviceName": "UPS Ground",
                          "totalCharges": 16.95,
                          "currency": "USD",
                          "transitDays": 3},
                "fixture": True}

    def _token(self):
        tok = http_form(
            "POST", "https://www.ups.com/security/v1/oauth/token",
            {"grant_type": "client_credentials"},
            basic_user=os.environ["UPS_CLIENT_ID"],
            basic_pass=os.environ["UPS_CLIENT_SECRET"])
        return tok["access_token"]

    def live(self):
        token = self._token()
        quote = http_json(
            "POST", "https://www.ups.com/api/rating/v1/Rate",
            headers={"Authorization": "Bearer " + token},
            body={
                "RateRequest": {
                    "Request": {"TransactionReference": {"CustomerContext": "stack"}},
                    "Shipment": {
                        "Shipper": {
                            "ShipperNumber": os.environ["UPS_ACCOUNT"],
                            "Address": {"PostalCode": "75207",
                                        "CountryCode": "US"}},
                        "ShipTo": {"Address": {"PostalCode": "75057",
                                               "CountryCode": "US"}},
                        "ShipFrom": {"Address": {"PostalCode": "75207",
                                                 "CountryCode": "US"}},
                        "Service": {"Code": "03"},
                        "Package": {"PackagingType": {"Code": "02"},
                                    "PackageWeight": {
                                        "UnitOfMeasurement": {"Code": "LBS"},
                                        "Weight": "5"}}}}})
        rated = (quote.get("RateResponse", {}).get("RatedShipment") or [{}])[0]
        charges = rated.get("TotalCharges", {})
        return {"action": "rate_quote",
                "serviceCode": "03", "serviceName": "UPS Ground",
                "totalCharges": charges.get("MonetaryValue"),
                "currency": charges.get("CurrencyCode")}
