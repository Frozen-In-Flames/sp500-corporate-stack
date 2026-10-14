# Integrations: the executable shared shelf (v0.2.0)

The v1 flywheel had one honest gap: the collective-action problem. Every
vendor would prefer the stack recommend it alone, in every category. V2
answers that with working code instead of argument. Twelve S&P 500 vendors
sit behind one shared adapter interface, and two cross-vendor workflows run
end to end across five and four vendors respectively. Shared shelf space is
demonstrated, not asserted.

## What shared shelf space means here

A vendor on the shelf does not own the workflow. The onboarding workflow
provisions identity at Microsoft, sends the welcome mail through Alphabet,
creates the HR contact in Salesforce, sends the SMS through Twilio, and
generates the offer letter through Adobe. Each vendor handles the step it is
best at, inside a workflow the stack defines. That is the shelf: one
interface, many vendors, no exclusivity.

## The adapter contract

`integrations/adapter.py` defines the `Adapter` base class. Every adapter
sets:

- `ticker` (verified against `data/constituents.csv`, never guessed),
  `vendor`, `category`, `product`, `api_name`, `docs_url`
- `env_keys`: the environment variables that activate live mode
- `capabilities()`: what the vendor can do from this adapter
- `demo()`: a fixture-backed result. Always works, $0, no credentials
- `live()`: one real endpoint call against the vendor's public API

`run()` picks live when every env key is present, otherwise demo. Nothing
is committed with keys; live mode is strictly opt-in per vendor.

## The twelve adapters

| Ticker | Vendor | Category | Live call |
|---|---|---|---|
| MSFT | Microsoft | identity | Graph `GET /me` |
| CRM | Salesforce | crm | create Contact (REST v60) |
| TWLO | Twilio | voip_telephony | send SMS (Messages API) |
| INTU | Intuit | accounting | create Invoice (QBO sandbox) |
| ADBE | Adobe | document_management | HTML to PDF (PDF Services) |
| AMZN | Amazon | compute | STS GetCallerIdentity (SigV4, stdlib) |
| GOOGL | Alphabet | productivity_suite | Gmail send |
| V | Visa | payments_processing | Visa Direct push funds (sandbox, mutual TLS) |
| FDX | FedEx | parcel_shipping | rate quote (Rate API v1) |
| UPS | UPS | parcel_shipping | rate quote (Rating API v1) |
| CSCO | Cisco | team_messaging | post Webex message |
| PYPL | PayPal | payments_processing | create order (sandbox) |

FedEx and UPS share the shipping category on purpose: competing vendors on
the same shelf is the point. All live calls use only the Python standard
library (urllib, hmac, ssl). No pip packages, no SDKs.

## Environment keys for live mode

| Adapter | Env keys |
|---|---|
| MSFT | `MS_GRAPH_TOKEN` |
| CRM | `SF_INSTANCE_URL`, `SF_ACCESS_TOKEN` |
| TWLO | `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_FROM`, `TWILIO_TO` |
| INTU | `QBO_ACCESS_TOKEN`, `QBO_REALM_ID` |
| ADBE | `ADOBE_ACCESS_TOKEN` |
| AMZN | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| GOOGL | `GOOGLE_ACCESS_TOKEN`, `GOOGLE_SENDER`, `GOOGLE_RECIPIENT` |
| V | `VISA_USER`, `VISA_PASS`, `VISA_CERT`, `VISA_KEY` |
| FDX | `FEDEX_CLIENT_ID`, `FEDEX_CLIENT_SECRET`, `FEDEX_ACCOUNT` |
| UPS | `UPS_CLIENT_ID`, `UPS_CLIENT_SECRET`, `UPS_ACCOUNT` |
| CSCO | `WEBEX_TOKEN`, `WEBEX_ROOM_ID` |
| PYPL | `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET` |

Tokens are bearer or OAuth credentials you create in each vendor's free
developer tier or sandbox. Set them, rerun, and the same workflow executes
live calls where keys exist and demo fixtures where they do not. Mixed mode
is the normal state: the shelf degrades gracefully per vendor.

## The actualization mechanism

This is how a vendor opts into the shelf: maintain an adapter. The contract
is twelve lines of metadata plus one real endpoint. A vendor that keeps its
adapter current gets its product inside every workflow the stack ships, in
front of every adopting company. Certification in v1 was a badge; in v2 it
is a pull request. The incentive is the same customer-acquisition channel
the flywheel describes, now with a concrete integration artifact instead of
a logo.

## Workflows

- `workflows/onboarding.py`: new-employee onboarding, 5 vendors
  (MSFT, GOOGL, CRM, TWLO, ADBE).
- `workflows/order_to_cash.py`: order to cash, 4 vendors
  (PYPL, FDX, INTU, CSCO).

Run them: `python3 -m integrations.shelf run onboarding`.

## Honest limits

- Demo fixtures mirror real response shapes but are fixtures. The demo page
  labels its workflow run as a recorded demo-mode run.
- Live calls were written against each vendor's public docs (October 2026)
  but have not been executed against paid accounts here; OAuth token
  plumbing (Intuit, FedEx, UPS, PayPal) follows each vendor's documented
  flow and should be verified with real sandbox credentials before any
  production claim.
- Visa Direct live mode needs a client certificate from Visa Developer;
  without it, the adapter stays in demo mode like the rest.
- Twelve vendors is a proof of the shelf, not the shelf. The mapped set is
  278; the adapter pattern is what scales.
