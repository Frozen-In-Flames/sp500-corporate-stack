"""Twilio (TWLO) adapter: programmable messaging."""

import os

from ..adapter import Adapter, http_form


class TwilioAdapter(Adapter):
    ticker = "TWLO"
    vendor = "Twilio"
    category = "voip_telephony"
    product = "Programmable Messaging (SMS)"
    api_name = "Twilio REST API 2010-04-01"
    docs_url = "https://www.twilio.com/docs/messaging/api"
    env_keys = ("TWILIO_SID", "TWILIO_TOKEN", "TWILIO_FROM", "TWILIO_TO")

    def capabilities(self):
        return ["send SMS",
                "two-factor and notification messaging",
                "voice calls (same API family)"]

    def demo(self):
        return {"action": "send_sms",
                "message": {"sid": "demo-SM-message-sid",
                            "to": "+15550001111",
                            "from_": "+15550002222",
                            "body": "Welcome to the stack, Ava. Day one starts Monday.",
                            "status": "queued"},
                "fixture": True}

    def live(self):
        sid = os.environ["TWILIO_SID"]
        resp = http_form(
            "POST",
            "https://api.twilio.com/2010-04-01/Accounts/%s/Messages.json" % sid,
            {"To": os.environ["TWILIO_TO"],
             "From": os.environ["TWILIO_FROM"],
             "Body": "Welcome to the stack. Day one starts Monday."},
            basic_user=sid, basic_pass=os.environ["TWILIO_TOKEN"])
        return {"action": "send_sms", "sid": resp.get("sid"),
                "status": resp.get("status"), "to": resp.get("to")}
