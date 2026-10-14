window.SHELF = [
 {
  "ticker": "MSFT",
  "vendor": "Microsoft",
  "category": "identity",
  "product": "Microsoft Entra ID via Microsoft Graph",
  "api": "Microsoft Graph v1.0",
  "docs": "https://learn.microsoft.com/en-us/graph/api/overview",
  "capabilities": [
   "directory identity (users, groups)",
   "mail and calendar via Graph",
   "onboarding account provisioning"
  ],
  "env_keys": [
   "MS_GRAPH_TOKEN"
  ],
  "live_ready": false
 },
 {
  "ticker": "CRM",
  "vendor": "Salesforce",
  "category": "crm",
  "product": "Sales Cloud",
  "api": "Salesforce REST API v60.0",
  "docs": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/",
  "capabilities": [
   "create and query CRM records (leads, contacts, accounts)",
   "pipeline and opportunity objects"
  ],
  "env_keys": [
   "SF_INSTANCE_URL",
   "SF_ACCESS_TOKEN"
  ],
  "live_ready": false
 },
 {
  "ticker": "TWLO",
  "vendor": "Twilio",
  "category": "voip_telephony",
  "product": "Programmable Messaging (SMS)",
  "api": "Twilio REST API 2010-04-01",
  "docs": "https://www.twilio.com/docs/messaging/api",
  "capabilities": [
   "send SMS",
   "two-factor and notification messaging",
   "voice calls (same API family)"
  ],
  "env_keys": [
   "TWILIO_SID",
   "TWILIO_TOKEN",
   "TWILIO_FROM",
   "TWILIO_TO"
  ],
  "live_ready": false
 },
 {
  "ticker": "INTU",
  "vendor": "Intuit",
  "category": "accounting",
  "product": "QuickBooks Online",
  "api": "QuickBooks Online Accounting API (sandbox)",
  "docs": "https://developer.intuit.com/app/developer/qbo/docs/get-started",
  "capabilities": [
   "create invoices and bills",
   "customer and vendor records",
   "profit-and-loss reports"
  ],
  "env_keys": [
   "QBO_ACCESS_TOKEN",
   "QBO_REALM_ID"
  ],
  "live_ready": false
 },
 {
  "ticker": "ADBE",
  "vendor": "Adobe",
  "category": "document_management",
  "product": "Adobe PDF Services",
  "api": "PDF Services API v2 (htmltopdf)",
  "docs": "https://developer.adobe.com/document-services/docs/overview/pdf-services-api/",
  "capabilities": [
   "HTML to PDF generation",
   "PDF manipulation (merge, split, compress)"
  ],
  "env_keys": [
   "ADOBE_ACCESS_TOKEN"
  ],
  "live_ready": false
 },
 {
  "ticker": "AMZN",
  "vendor": "Amazon",
  "category": "compute",
  "product": "AWS",
  "api": "AWS STS GetCallerIdentity (SigV4)",
  "docs": "https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html",
  "capabilities": [
   "identity verification via STS",
   "S3, EC2 and the full AWS API family (same signing)"
  ],
  "env_keys": [
   "AWS_ACCESS_KEY_ID",
   "AWS_SECRET_ACCESS_KEY"
  ],
  "live_ready": false
 },
 {
  "ticker": "GOOGL",
  "vendor": "Alphabet",
  "category": "productivity_suite",
  "product": "Gmail",
  "api": "Gmail API v1",
  "docs": "https://developers.google.com/gmail/api/reference/rest",
  "capabilities": [
   "send mail",
   "calendar events (same OAuth scope family)"
  ],
  "env_keys": [
   "GOOGLE_ACCESS_TOKEN",
   "GOOGLE_SENDER",
   "GOOGLE_RECIPIENT"
  ],
  "live_ready": false
 },
 {
  "ticker": "V",
  "vendor": "Visa",
  "category": "payments_processing",
  "product": "Visa Direct",
  "api": "Visa Direct Funds Transfer API (sandbox)",
  "docs": "https://developer.visa.com/capabilities/visa_direct",
  "capabilities": [
   "push funds to a card (payouts, refunds)",
   "pull funds (collections)"
  ],
  "env_keys": [
   "VISA_USER",
   "VISA_PASS",
   "VISA_CERT",
   "VISA_KEY"
  ],
  "live_ready": false
 },
 {
  "ticker": "FDX",
  "vendor": "FedEx",
  "category": "parcel_shipping",
  "product": "FedEx Web Services",
  "api": "FedEx Rate API v1",
  "docs": "https://developer.fedex.com/api/en-us/catalog/rate/v1/docs.html",
  "capabilities": [
   "rate quotes",
   "shipment creation and tracking (same API family)"
  ],
  "env_keys": [
   "FEDEX_CLIENT_ID",
   "FEDEX_CLIENT_SECRET",
   "FEDEX_ACCOUNT"
  ],
  "live_ready": false
 },
 {
  "ticker": "UPS",
  "vendor": "UPS",
  "category": "parcel_shipping",
  "product": "UPS Developer APIs",
  "api": "UPS Rating API v1",
  "docs": "https://developer.ups.com/api/reference?loc=en_US#operation/Rate",
  "capabilities": [
   "rate quotes",
   "shipment creation and tracking (same API family)"
  ],
  "env_keys": [
   "UPS_CLIENT_ID",
   "UPS_CLIENT_SECRET",
   "UPS_ACCOUNT"
  ],
  "live_ready": false
 },
 {
  "ticker": "CSCO",
  "vendor": "Cisco",
  "category": "team_messaging",
  "product": "Webex",
  "api": "Webex REST API v1",
  "docs": "https://developer.webex.com/docs/api/v1/messages",
  "capabilities": [
   "post messages to rooms",
   "create meetings (same API family)"
  ],
  "env_keys": [
   "WEBEX_TOKEN",
   "WEBEX_ROOM_ID"
  ],
  "live_ready": false
 },
 {
  "ticker": "PYPL",
  "vendor": "PayPal",
  "category": "payments_processing",
  "product": "PayPal Checkout",
  "api": "PayPal Orders API v2 (sandbox)",
  "docs": "https://developer.paypal.com/docs/api/orders/v2/",
  "capabilities": [
   "create and capture checkout orders",
   "payouts (same API family)"
  ],
  "env_keys": [
   "PAYPAL_CLIENT_ID",
   "PAYPAL_SECRET"
  ],
  "live_ready": false
 }
];