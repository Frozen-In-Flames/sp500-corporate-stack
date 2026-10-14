window.WORKFLOW_TRANSCRIPT = {
 "name": "New-employee onboarding",
 "description": "Provision a new hire across identity, mail, CRM, messaging, and documents.",
 "steps": [
  {
   "step": 1,
   "action": "provision identity account",
   "ticker": "MSFT",
   "vendor": "Microsoft",
   "category": "identity",
   "product": "Microsoft Entra ID via Microsoft Graph",
   "mode": "demo",
   "result": {
    "action": "provision_user",
    "user": {
     "displayName": "Ava Reyes",
     "userPrincipalName": "ava.reyes@example.com",
     "id": "demo-9f31-user-id",
     "accountEnabled": true
    },
    "fixture": true
   }
  },
  {
   "step": 2,
   "action": "send welcome email",
   "ticker": "GOOGL",
   "vendor": "Alphabet",
   "category": "productivity_suite",
   "product": "Gmail",
   "mode": "demo",
   "result": {
    "action": "send_mail",
    "message": {
     "id": "demo-gmail-msg-id",
     "threadId": "demo-thread-id",
     "labelIds": [
      "SENT"
     ]
    },
    "fixture": true
   }
  },
  {
   "step": 3,
   "action": "create HR contact record",
   "ticker": "CRM",
   "vendor": "Salesforce",
   "category": "crm",
   "product": "Sales Cloud",
   "mode": "demo",
   "result": {
    "action": "create_contact",
    "record": {
     "Id": "demo-003-contact-id",
     "LastName": "Reyes",
     "FirstName": "Ava",
     "Email": "ava.reyes@example.com"
    },
    "fixture": true
   }
  },
  {
   "step": 4,
   "action": "send welcome SMS",
   "ticker": "TWLO",
   "vendor": "Twilio",
   "category": "voip_telephony",
   "product": "Programmable Messaging (SMS)",
   "mode": "demo",
   "result": {
    "action": "send_sms",
    "message": {
     "sid": "demo-SM-message-sid",
     "to": "+15550001111",
     "from_": "+15550002222",
     "body": "Welcome to the stack, Ava. Day one starts Monday.",
     "status": "queued"
    },
    "fixture": true
   }
  },
  {
   "step": 5,
   "action": "generate offer letter PDF",
   "ticker": "ADBE",
   "vendor": "Adobe",
   "category": "document_management",
   "product": "Adobe PDF Services",
   "mode": "demo",
   "result": {
    "action": "htmltopdf",
    "document": {
     "assetID": "demo-urn-pdf-asset",
     "downloadUri": "https://demo.invalid/offer-letter.pdf",
     "pages": 2
    },
    "fixture": true
   }
  }
 ],
 "vendors": [
  "ADBE",
  "CRM",
  "GOOGL",
  "MSFT",
  "TWLO"
 ],
 "modes": [
  "demo"
 ]
};