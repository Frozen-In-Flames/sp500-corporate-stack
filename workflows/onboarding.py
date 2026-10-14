"""New-employee onboarding across five S&P 500 vendors on the shared shelf.

Microsoft provisions identity, Google sends the welcome mail, Salesforce
creates the HR contact, Twilio sends the welcome SMS, Adobe generates the
offer letter PDF. Five vendors, one workflow, no vendor owns the shelf.
"""

WORKFLOW = {
    "name": "New-employee onboarding",
    "description": ("Provision a new hire across identity, mail, CRM, "
                    "messaging, and documents."),
    "steps": [
        {"step": 1, "adapter": "MSFT",
         "action": "provision identity account"},
        {"step": 2, "adapter": "GOOGL",
         "action": "send welcome email"},
        {"step": 3, "adapter": "CRM",
         "action": "create HR contact record"},
        {"step": 4, "adapter": "TWLO",
         "action": "send welcome SMS"},
        {"step": 5, "adapter": "ADBE",
         "action": "generate offer letter PDF"},
    ],
}
