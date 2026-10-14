"""Pull REIT total assets from SEC EDGAR companyfacts and cache.

Free public API; proper User-Agent set in live_data. Writes
data/reit_values.json (used as fallback by stack_builder --tier3).

The figure is total assets from the latest 10-K, a labeled proxy for
property portfolio scale. Never presented as appraised property value.

Usage: python3 scripts/pull_reit_values.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import live_data


def main():
    with open(os.path.join(live_data.DATA_DIR, "vendor_map.json")) as f:
        mappings = json.load(f)["mappings"]
    reits = [(m["ticker"], m["name"]) for m in mappings
             if m.get("status") == "unmapped"
             and m.get("reason_code") == "reit"]
    print("pulling %d REITs" % len(reits))
    data = live_data.fetch_reit_assets(reits)
    live_data.save_reit_cache(data)
    n = sum(1 for r in data.values() if r.get("total_assets_usd"))
    print("cached %d REITs, %d with asset values -> %s"
          % (len(data), n, live_data.REIT_CACHE))


if __name__ == "__main__":
    main()
