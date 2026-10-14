# S&P 500 Corporate Stack

A reference tech stack that maps what a new business needs onto vendors inside
the S&P 500, diversified so no single vendor dominates. The thesis: a company
at scale buys across roughly sixty capability categories (cloud, payroll,
insurance, shipping, travel, legal, and the rest). Route that spend through
index vendors and the operating budget becomes diversified revenue for S&P 500
companies, which is the flywheel described in [flywheel.md](flywheel.md).

## v0.4.0: tier 3, quantified

Tier 3 was the named boundary: 190 companies with no routable corporate
spend. v0.4.0 quantifies it through the channels that do touch it, live.
`python3 stack_builder.py --tier3` pulls real current numbers at runtime:
federal obligated award dollars per company per fiscal year from
USAspending.gov (federal only, matched by recipient name), and total assets
from the latest 10-K on SEC EDGAR for the 8 REITs (a labeled proxy for
property portfolio scale, never appraised value). Cached JSON is fallback
only, always labeled with its date; `--refresh` forces a fresh pull and
rewrites the cache. Every one of the 190 carries a reason code
(defense_gov, reit, pharma, semis, commodities, other), and the demo page
shows the tier-3 breakdown by reason code with dollar figures. The 190 are
not $0 of economic reality; they are $0 of routable corporate spend, and now
the difference is measured.

## v0.3.0: the three tiers

The relativity between the three coverage tiers is now explicit and complete.
Every one of the 278 mapped vendors carries a `consumer_channels` field:
their consumer-facing presence (157 have one, 121 are honestly empty, pure
B2B). The 32 indirect vendors are a first-class Consumer & Perks shelf across
12 perk categories (cruises, dining, streaming, apparel, footwear, beauty,
home goods, beverages, snacks, packaged foods, toys and games, wearables).
The builder now prints an employee-perks shelf alongside the enterprise stack,
and `python3 stack_builder.py --relativity` prints the three-tier report:
tier 1 is direct enterprise procurement, tier 2 is employee-directed consumer
spend reaching companies the enterprise stack cannot touch, tier 3 is the 190
companies with no routable spend, the named boundary that keeps the other two
tiers honest. The demo page has a three-tier visualization.

## v0.2.0: the shelf is executable

Twelve S&P 500 vendors now sit behind one shared adapter interface in
`integrations/`, each with a real developer API wired for live calls and a
fixture-backed demo mode that runs with $0 and no credentials. Two
cross-vendor workflows ship in `workflows/`: new-employee onboarding across
five vendors (Microsoft, Alphabet, Salesforce, Twilio, Adobe) and
order-to-cash across four (PayPal, FedEx, Intuit, Cisco). Run them with
`python3 -m integrations.shelf run onboarding`. The demo page has a V2
panel with the vendor grid and a recorded run of the onboarding workflow.
Full contract, env key table, and honest limits are in
[INTEGRATIONS.md](INTEGRATIONS.md).

## Honest coverage numbers (v0.1.0)

Of 500 index companies (503 index lines; Alphabet, Fox Corp, and News Corp
each have two share classes):

- **278 mapped**: sell at least one product or service a business can buy.
- **32 indirect**: consumer-only, but usable as corporate employee perks.
- **190 unmapped**: sell nothing a business can buy. No force-fitting.

The literal "all 500" does not hold and this repo does not pretend it does.
Commodity producers, pure consumer brands, defense contractors selling only to
governments, and REITs with no enterprise offering are marked unmapped, with
the reason noted per company in `data/vendor_map.json`.

Known taxonomy gaps (real enterprise products with no fitting category in v1):
CAD/PLM software (Autodesk), virtualization (Broadcom/VMware), on-prem
storage arrays, credit and risk scoring (FICO). These are documented, not
hidden, and are candidates for v0.2.0 categories.

## How the builder works

`stack_builder.py` takes a company size band and industry, then for each of
61 capability categories picks one primary vendor from the mapped set using a
greedy least-used-vendor rule, which maximizes vendor spread deterministically.
A spend model estimates annual cost per category from company headcount
(sublinear scaling for infrastructure, linear for per-seat items), adjusted by
industry relevance weights. Output: the recommended stack, categories covered,
distinct S&P 500 vendors used, estimated total annual spend, estimated revenue
directed to S&P 500 vendors, top-vendor concentration, and any uncovered
categories.

```bash
python3 stack_builder.py --size smb --industry technology
python3 stack_builder.py --size enterprise --industry retail --format json
python3 stack_builder.py --coverage
python3 stack_builder.py --relativity
```

Example: a 200-person tech SMB gets 55 categories covered across 46 index
vendors, directing roughly $7.8M in annual operating spend toward the index.

## Demo

Open `demo/index.html` in a browser (no build step). Pick a size band and
industry to explore the recommended stack.

## Repo layout

- `data/constituents.csv`: 500 companies, ticker, name, GICS sector and
  sub-industry.
- `data/categories.json`: 61 business capability categories.
- `data/vendor_map.json`: per-company mapping with status
  (mapped/indirect/unmapped), specific products, notes, `consumer_channels`
  for mapped vendors, `perk_assignments` for indirect vendors, and
  `reason_code` for unmapped vendors (defense_gov, reit, pharma, semis,
  commodities, other).
- `data/gov_awards.json`: cached federal award totals per company per fiscal
  year (USAspending.gov), fallback only, labeled with pull date.
- `data/reit_values.json`: cached REIT total assets from latest 10-K
  (SEC EDGAR), fallback only, labeled with pull date.
- `live_data.py`: live-first tier-3 quantification (USAspending + SEC EDGAR
  at runtime, cache fallback, `--refresh` rewrites cache).
- `data/perk_categories.json`: the 12 Consumer & Perks shelf categories.
- `stack_builder.py`: the recommendation engine and spend model.
- `demo/`: static demo page plus generated data.
- `flywheel.md`: the business model, including an honest account of where the
  loop is strong and where it is narrative.
- `integrations/`: v0.2.0 executable shelf, twelve vendor adapters behind one
  contract, demo mode by default, live mode via env keys.
- `workflows/`: v0.2.0 cross-vendor workflows (onboarding, order-to-cash).
- `INTEGRATIONS.md`: the adapter contract, env key table, and honest limits.

## Data sources

- S&P 500 constituents: Wikipedia, "List of S&P 500 companies," retrieved
  October 13, 2026. Constituents change; the retrieval date is recorded in
  `data/vendor_map.json`.
- Product mappings: vendor documentation and product pages, verified by web
  search for anchor and ambiguous companies (October 2026). Specific product
  names are recorded per mapping so anyone can check them.
- Spend figures: order-of-magnitude planning estimates, not quotes.
- Tier-3 federal awards: USAspending.gov
  `/api/v2/search/spending_by_category/recipient/`, pulled live at runtime
  by `stack_builder.py --tier3` (fiscal years 2023-2025), matched by
  recipient name; federal obligations only, excludes state/local.
- Tier-3 REIT scale: SEC EDGAR companyfacts, total assets from the latest
  10-K, a labeled proxy for property portfolio scale, never appraised
  property value.

## License

Apache-2.0. Not investment advice.
