"""Adobe (ADBE) adapter: PDF Services, HTML to PDF generation."""

import base64
import os
import time
import urllib.request

from ..adapter import Adapter, AdapterError, http_json


class AdobeAdapter(Adapter):
    ticker = "ADBE"
    vendor = "Adobe"
    category = "document_management"
    product = "Adobe PDF Services"
    api_name = "PDF Services API v2 (htmltopdf)"
    docs_url = "https://developer.adobe.com/document-services/docs/overview/pdf-services-api/"
    env_keys = ("ADOBE_ACCESS_TOKEN",)

    def capabilities(self):
        return ["HTML to PDF generation",
                "PDF manipulation (merge, split, compress)"]

    def demo(self):
        return {"action": "htmltopdf",
                "document": {"assetID": "demo-urn-pdf-asset",
                             "downloadUri": "https://demo.invalid/offer-letter.pdf",
                             "pages": 2},
                "fixture": True}

    def live(self):
        token = os.environ["ADOBE_ACCESS_TOKEN"]
        auth = {"Authorization": "Bearer " + token}
        # 1. Reserve an upload asset.
        asset = http_json("POST",
                          "https://pdf-services.adobe.io/assets",
                          headers=auth,
                          body={"mediaType": "text/html"})
        upload_uri = asset.get("uploadUri")
        asset_id = asset.get("assetID")
        if not upload_uri or not asset_id:
            raise AdapterError("Adobe asset reservation returned no uploadUri")
        # 2. Upload the HTML.
        html = (b"<html><body><h1>Offer Letter</h1>"
                b"<p>Welcome to the stack.</p></body></html>")
        req = urllib.request.Request(upload_uri, data=html,
                                     headers={"Content-Type": "text/html"},
                                     method="PUT")
        urllib.request.urlopen(req, timeout=20).read()
        # 3. Run the htmltopdf job.
        job = http_json("POST",
                        "https://pdf-services.adobe.io/operation/htmltopdf",
                        headers=auth,
                        body={"assetID": asset_id,
                              "json": {"includeHeaderFooter": False}})
        job_uri = job.get("statusUri") or job.get("jobUri")
        # 4. Poll for completion (bounded).
        result = None
        for _ in range(12):
            time.sleep(5)
            status = http_json("GET", job_uri, headers=auth)
            if status.get("status") == "done":
                result = status.get("asset", {})
                break
        if result is None:
            raise AdapterError("Adobe htmltopdf job did not finish in time")
        return {"action": "htmltopdf", "assetID": result.get("assetID"),
                "downloadUri": result.get("downloadUri")}
