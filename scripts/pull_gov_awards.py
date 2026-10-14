"""Pull federal award totals for tier-3 companies from USAspending.gov and cache.

Free public API, no key. Writes data/gov_awards.json (used as fallback by
stack_builder --tier3; live pull is the default at runtime).

Usage: python3 scripts/pull_gov_awards.py [--fiscal-years 2023,2024,2025]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import live_data


def main():
    fys = live_data.FISCAL_YEARS
    for a in sys.argv[1:]:
        if a.startswith("--fiscal-years"):
            fys = [int(x) for x in a.split("=", 1)[1].split(",")]
    with open(os.path.join(live_data.DATA_DIR, "vendor_map.json")) as f:
        mappings = json.load(f)["mappings"]
    tier3 = [(m["ticker"], m["name"]) for m in mappings
             if m.get("status") == "unmapped"]
    print("pulling %d tier-3 companies, FYs %s" % (len(tier3), fys))
    data = live_data.fetch_gov_awards(tier3, fiscal_years=fys)
    doc = live_data.save_awards_cache(data, fiscal_years=fys)
    n = sum(1 for c in data.values() if any(v for v in c["by_year"].values()))
    print("cached %d companies, %d with nonzero awards -> %s"
          % (len(data), n, live_data.AWARDS_CACHE))


if __name__ == "__main__":
    main()
