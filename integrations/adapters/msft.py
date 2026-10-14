"""Microsoft (MSFT) adapter: Microsoft Graph, identity and productivity."""

import os

from ..adapter import Adapter, http_json


class MicrosoftAdapter(Adapter):
    ticker = "MSFT"
    vendor = "Microsoft"
    category = "identity"
    product = "Microsoft Entra ID via Microsoft Graph"
    api_name = "Microsoft Graph v1.0"
    docs_url = "https://learn.microsoft.com/en-us/graph/api/overview"
    env_keys = ("MS_GRAPH_TOKEN",)

    def capabilities(self):
        return ["directory identity (users, groups)",
                "mail and calendar via Graph",
                "onboarding account provisioning"]

    def demo(self):
        return {"action": "provision_user",
                "user": {"displayName": "Ava Reyes",
                         "userPrincipalName": "ava.reyes@example.com",
                         "id": "demo-9f31-user-id",
                         "accountEnabled": True},
                "fixture": True}

    def live(self):
        token = os.environ["MS_GRAPH_TOKEN"]
        me = http_json("GET", "https://graph.microsoft.com/v1.0/me",
                       headers={"Authorization": "Bearer " + token})
        return {"action": "graph_me",
                "displayName": me.get("displayName"),
                "userPrincipalName": me.get("userPrincipalName"),
                "id": me.get("id")}
