# S&P 500 Corporate Stack

A reference tech stack that maps what a new business needs onto vendors inside
the S&P 500, diversified so no single vendor dominates. The thesis: a company
at scale buys across roughly sixty capability categories (cloud, payroll,
insurance, shipping, travel, legal, and the rest). Route that spend through
index vendors and the operating budget becomes diversified revenue for S&P 500
companies, which is the flywheel described in [flywheel.md](flywheel.md).

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
  (mapped/indirect/unmapped), specific products, and notes.
- `stack_builder.py`: the recommendation engine and spend model.
- `demo/`: static demo page plus generated data.
- `flywheel.md`: the business model, including an honest account of where the
  loop is strong and where it is narrative.

## Data sources

- S&P 500 constituents: Wikipedia, "List of S&P 500 companies," retrieved
  October 13, 2026. Constituents change; the retrieval date is recorded in
  `data/vendor_map.json`.
- Product mappings: vendor documentation and product pages, verified by web
  search for anchor and ambiguous companies (October 2026). Specific product
  names are recorded per mapping so anyone can check them.
- Spend figures: order-of-magnitude planning estimates, not quotes.

## License

Apache-2.0. Not investment advice.
