"""Cisco (CSCO) adapter: Webex messaging."""

import os

from ..adapter import Adapter, http_json


class WebexAdapter(Adapter):
    ticker = "CSCO"
    vendor = "Cisco"
    category = "team_messaging"
    product = "Webex"
    api_name = "Webex REST API v1"
    docs_url = "https://developer.webex.com/docs/api/v1/messages"
    env_keys = ("WEBEX_TOKEN", "WEBEX_ROOM_ID")

    def capabilities(self):
        return ["post messages to rooms",
                "create meetings (same API family)"]

    def demo(self):
        return {"action": "post_message",
                "message": {"id": "demo-webex-msg-id",
                            "roomId": "demo-room-id",
                            "text": "Order #1042 paid and labeled. Ship it.",
                            "created": "2026-10-13T00:00:00.000Z"},
                "fixture": True}

    def live(self):
        msg = http_json(
            "POST", "https://webexapis.com/v1/messages",
            headers={"Authorization": "Bearer " + os.environ["WEBEX_TOKEN"]},
            body={"roomId": os.environ["WEBEX_ROOM_ID"],
                  "text": "Stack workflow ping: order paid and labeled."})
        return {"action": "post_message", "id": msg.get("id"),
                "roomId": msg.get("roomId")}
