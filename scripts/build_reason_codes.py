"""Assign a reason_code to every unmapped (tier 3) company in vendor_map.json.

Reason codes: defense_gov, reit, pharma, semis, commodities, other.
Deterministic rules from GICS sub_industry; the existing human-written
'note' field stays as the one-line explanation.

Usage: python3 scripts/build_reason_codes.py [--check]
  --check: verify every unmapped entry already has a valid reason_code.
"""

import csv
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMMODITY_SUBS = {
    "Oil & Gas Exploration & Production",
    "Oil & Gas Storage & Transportation",
    "Oil & Gas Equipment & Services",
    "Oil & Gas Refining & Marketing",
    "Oil & Gas Drilling",
    "Integrated Oil & Gas",
    "Steel",
    "Copper",
    "Gold",
    "Silver",
    "Aluminum",
    "Diversified Metals & Mining",
    "Fertilizers & Agricultural Chemicals",
    "Agricultural Products & Services",
    "Construction Materials",
    "Paper & Plastic Packaging Products & Materials",
    "Paper Products",
    "Forest Products",
    "Specialty Chemicals",
    "Diversified Chemicals",
    "Commodity Chemicals",
    "Industrial Gases",
    "Metal, Glass & Plastic Containers",
}

VALID_CODES = {"defense_gov", "reit", "pharma", "semis", "commodities", "other"}


def reason_code(sub_industry):
    s = (sub_industry or "").strip()
    if "REIT" in s:
        return "reit"
    if s == "Aerospace & Defense":
        return "defense_gov"
    if s in ("Pharmaceuticals", "Biotechnology"):
        return "pharma"
    if s in ("Semiconductors", "Semiconductor Materials & Equipment"):
        return "semis"
    if s in COMMODITY_SUBS:
        return "commodities"
    return "other"


def load():
    with open(os.path.join(REPO, "data", "vendor_map.json")) as f:
        vendor_map = json.load(f)
    cons = {}
    with open(os.path.join(REPO, "data", "constituents.csv")) as f:
        for row in csv.DictReader(f):
            cons[row["ticker"]] = row
    return vendor_map, cons


def main():
    check_only = "--check" in sys.argv
    vendor_map, cons = load()
    changed = 0
    for m in vendor_map["mappings"]:
        if m.get("status") != "unmapped":
            continue
        sub = cons.get(m["ticker"], {}).get("sub_industry", "")
        code = reason_code(sub)
        assert code in VALID_CODES, code
        if check_only:
            if m.get("reason_code") != code:
                print("MISMATCH %s: stored=%r computed=%r (sub=%r)" % (
                    m["ticker"], m.get("reason_code"), code, sub))
                sys.exit(1)
        elif m.get("reason_code") != code:
            m["reason_code"] = code
            changed += 1
    if check_only:
        print("reason codes OK")
        return
    with open(os.path.join(REPO, "data", "vendor_map.json"), "w") as f:
        json.dump(vendor_map, f, indent=2)
        f.write("\n")
    print("assigned reason codes, %d entries updated" % changed)


if __name__ == "__main__":
    main()
