"""FedEx (FDX) adapter: rate quotes via the Rate API."""

import os

from ..adapter import Adapter, http_form, http_json


class FedExAdapter(Adapter):
    ticker = "FDX"
    vendor = "FedEx"
    category = "parcel_shipping"
    product = "FedEx Web Services"
    api_name = "FedEx Rate API v1"
    docs_url = "https://developer.fedex.com/api/en-us/catalog/rate/v1/docs.html"
    env_keys = ("FEDEX_CLIENT_ID", "FEDEX_CLIENT_SECRET",
                "FEDEX_ACCOUNT")

    def capabilities(self):
        return ["rate quotes",
                "shipment creation and tracking (same API family)"]

    def demo(self):
        return {"action": "rate_quote",
                "quote": {"serviceType": "FEDEX_GROUND",
                          "totalNetCharge": 18.42,
                          "currency": "USD",
                          "transitDays": 3},
                "fixture": True}

    def _token(self):
        tok = http_form(
            "POST", "https://apis.fedex.com/oauth/token",
            {"grant_type": "client_credentials",
             "client_id": os.environ["FEDEX_CLIENT_ID"],
             "client_secret": os.environ["FEDEX_CLIENT_SECRET"]})
        return tok["access_token"]

    def live(self):
        token = self._token()
        quote = http_json(
            "POST", "https://apis.fedex.com/rate/v1/rates/quotes",
            headers={"Authorization": "Bearer " + token},
            body={
                "accountNumber": {"value": os.environ["FEDEX_ACCOUNT"]},
                "requestedShipment": {
                    "shipper": {"address": {"postalCode": "75207",
                                            "countryCode": "US"}},
                    "recipient": {"address": {"postalCode": "75057",
                                              "countryCode": "US"}},
                    "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                    "rateRequestType": ["LIST"],
                    "requestedPackageLineItems": [{
                        "weight": {"units": "LB", "value": 5}}]}})
        details = (quote.get("output", {}).get("rateReplyDetails") or [{}])[0]
        charge = ((details.get("ratedShipmentDetails") or [{}])[0]
                  .get("totalNetCharge"))
        return {"action": "rate_quote",
                "serviceType": details.get("serviceType"),
                "totalNetCharge": charge,
                "currency": "USD"}
