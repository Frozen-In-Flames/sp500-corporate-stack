"""Alphabet (GOOGL) adapter: Gmail API, send a message."""

import base64
import os

from ..adapter import Adapter, http_json


class GoogleAdapter(Adapter):
    ticker = "GOOGL"
    vendor = "Alphabet"
    category = "productivity_suite"
    product = "Gmail"
    api_name = "Gmail API v1"
    docs_url = "https://developers.google.com/gmail/api/reference/rest"
    env_keys = ("GOOGLE_ACCESS_TOKEN", "GOOGLE_SENDER", "GOOGLE_RECIPIENT")

    def capabilities(self):
        return ["send mail",
                "calendar events (same OAuth scope family)"]

    def demo(self):
        return {"action": "send_mail",
                "message": {"id": "demo-gmail-msg-id",
                            "threadId": "demo-thread-id",
                            "labelIds": ["SENT"]},
                "fixture": True}

    def live(self):
        token = os.environ["GOOGLE_ACCESS_TOKEN"]
        mime = ("From: %s\r\nTo: %s\r\nSubject: Welcome to the stack\r\n\r\n"
                "Day one starts Monday. Your accounts are provisioned."
                % (os.environ["GOOGLE_SENDER"],
                   os.environ["GOOGLE_RECIPIENT"]))
        raw = base64.urlsafe_b64encode(mime.encode()).decode()
        sent = http_json(
            "POST",
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={"Authorization": "Bearer " + token},
            body={"raw": raw})
        return {"action": "send_mail", "id": sent.get("id"),
                "threadId": sent.get("threadId")}
