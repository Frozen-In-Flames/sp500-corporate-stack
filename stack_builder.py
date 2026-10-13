#!/usr/bin/env python3
"""
S&P 500 Corporate Stack builder v1.

Reads data/vendor_map.json (honest per-company mapping of S&P 500
constituents to enterprise-buyable offerings) and produces a diversified
recommended vendor stack for a hypothetical new business.

Usage:
  python3 stack_builder.py --size smb --industry technology
  python3 stack_builder.py --size enterprise --industry retail --format json
  python3 stack_builder.py --coverage
  python3 stack_builder.py --emit-demo-data --out demo/stack_data.js
"""

import argparse
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

SIZE_BANDS = {
    "startup": {"label": "Startup (1-50 employees)", "employees": 25},
    "smb": {"label": "SMB (51-500 employees)", "employees": 200},
    "midmarket": {"label": "Mid-market (501-5,000 employees)", "employees": 2000},
    "enterprise": {"label": "Enterprise (5,000+ employees)", "employees": 15000},
}

INDUSTRIES = [
    "technology", "financial_services", "healthcare", "retail",
    "manufacturing", "hospitality", "professional_services",
]

# Per-category spend model. base = estimated annual USD for a 200-employee SMB.
# spend(employees) = base * (employees / 200) ** elasticity, when weight > 0.
# min_band: categories below this size band are skipped (0=startup..3=enterprise).
SPEND_MODEL = {
    "compute":              {"base": 300000, "elasticity": 0.80, "min_band": 0},
    "cloud_storage":        {"base": 60000,  "elasticity": 0.80, "min_band": 0},
    "productivity_suite":   {"base": 30000,  "elasticity": 1.00, "min_band": 0},
    "video_conferencing":   {"base": 40000,  "elasticity": 1.00, "min_band": 0},
    "team_messaging":       {"base": 20000,  "elasticity": 1.00, "min_band": 0},
    "voip_telephony":       {"base": 60000,  "elasticity": 1.00, "min_band": 1},
    "contact_center":       {"base": 24000,  "elasticity": 0.90, "min_band": 1},
    "crm":                  {"base": 60000,  "elasticity": 0.90, "min_band": 0},
    "erp":                  {"base": 150000, "elasticity": 0.70, "min_band": 1},
    "hcm":                  {"base": 60000,  "elasticity": 1.00, "min_band": 0},
    "payroll":              {"base": 70000,  "elasticity": 1.00, "min_band": 0},
    "benefits_admin":       {"base": 20000,  "elasticity": 1.00, "min_band": 1},
    "recruiting_ats":       {"base": 15000,  "elasticity": 0.70, "min_band": 0},
    "lms":                  {"base": 10000,  "elasticity": 1.00, "min_band": 2},
    "expense_management":   {"base": 30000,  "elasticity": 1.00, "min_band": 1},
    "accounting":           {"base": 25000,  "elasticity": 0.70, "min_band": 0},
    "tax_compliance":       {"base": 30000,  "elasticity": 0.70, "min_band": 0},
    "payments_processing":  {"base": 100000, "elasticity": 0.90, "min_band": 0},
    "corporate_cards":      {"base": 5000,   "elasticity": 1.00, "min_band": 1},
    "banking_treasury":     {"base": 20000,  "elasticity": 0.80, "min_band": 0},
    "lending":              {"base": 50000,  "elasticity": 0.90, "min_band": 1},
    "brokerage_401k":       {"base": 20000,  "elasticity": 1.00, "min_band": 1},
    "insurance_pc":         {"base": 100000, "elasticity": 0.90, "min_band": 0},
    "insurance_health":     {"base": 2400000,"elasticity": 1.00, "min_band": 0},
    "insurance_life":       {"base": 60000,  "elasticity": 1.00, "min_band": 1},
    "cybersecurity":        {"base": 20000,  "elasticity": 1.00, "min_band": 0},
    "iam":                  {"base": 16000,  "elasticity": 1.00, "min_band": 1},
    "data_warehouse":       {"base": 80000,  "elasticity": 0.80, "min_band": 1},
    "bi":                   {"base": 30000,  "elasticity": 0.90, "min_band": 1},
    "etl":                  {"base": 25000,  "elasticity": 0.80, "min_band": 1},
    "marketing_automation": {"base": 36000,  "elasticity": 0.80, "min_band": 0},
    "advertising":          {"base": 120000, "elasticity": 0.90, "min_band": 0},
    "ecommerce":            {"base": 24000,  "elasticity": 0.70, "min_band": 0},
    "cdn":                  {"base": 24000,  "elasticity": 0.70, "min_band": 1},
    "networking":           {"base": 50000,  "elasticity": 0.70, "min_band": 1},
    "devops":               {"base": 30000,  "elasticity": 0.80, "min_band": 0},
    "observability":        {"base": 40000,  "elasticity": 0.80, "min_band": 1},
    "itsm":                 {"base": 50000,  "elasticity": 0.80, "min_band": 2},
    "mdm":                  {"base": 12000,  "elasticity": 1.00, "min_band": 1},
    "endpoint_hardware":    {"base": 100000, "elasticity": 1.00, "min_band": 0},
    "backup_dr":            {"base": 30000,  "elasticity": 0.80, "min_band": 1},
    "database":             {"base": 50000,  "elasticity": 0.80, "min_band": 1},
    "ai_platform":          {"base": 40000,  "elasticity": 0.90, "min_band": 0},
    "esignature":           {"base": 20000,  "elasticity": 0.90, "min_band": 0},
    "legal":                {"base": 80000,  "elasticity": 0.70, "min_band": 0},
    "background_checks":    {"base": 4000,   "elasticity": 0.80, "min_band": 0},
    "corporate_travel":     {"base": 40000,  "elasticity": 1.00, "min_band": 1},
    "airlines":             {"base": 240000, "elasticity": 1.00, "min_band": 1},
    "hotels":               {"base": 160000, "elasticity": 1.00, "min_band": 1},
    "shipping_parcel":      {"base": 60000,  "elasticity": 0.90, "min_band": 0},
    "freight_logistics":    {"base": 80000,  "elasticity": 0.90, "min_band": 1},
    "fleet":                {"base": 80000,  "elasticity": 0.90, "min_band": 2},
    "office_supplies":      {"base": 100000, "elasticity": 1.00, "min_band": 0},
    "facilities":           {"base": 200000, "elasticity": 0.90, "min_band": 1},
    "real_estate":          {"base": 1600000,"elasticity": 0.90, "min_band": 1},
    "energy":               {"base": 120000, "elasticity": 0.90, "min_band": 1},
    "telecom":              {"base": 180000, "elasticity": 1.00, "min_band": 0},
    "water":                {"base": 12000,  "elasticity": 1.00, "min_band": 2},
    "foodservice":          {"base": 80000,  "elasticity": 1.00, "min_band": 1},
    "consulting":           {"base": 150000, "elasticity": 0.70, "min_band": 1},
    "employee_perks":       {"base": 200000, "elasticity": 1.00, "min_band": 1},
}

BAND_ORDER = ["startup", "smb", "midmarket", "enterprise"]

# Industry relevance multipliers per category (default 1.0; 0 = not needed).
INDUSTRY_WEIGHTS = {
    "technology": {"compute": 2.0, "devops": 2.0, "ai_platform": 2.0,
                   "observability": 2.0, "cloud_storage": 1.5, "cdn": 1.5,
                   "foodservice": 0.5, "fleet": 0.3, "freight_logistics": 0.3,
                   "hotels": 0.5},
    "financial_services": {"cybersecurity": 2.0, "iam": 2.0, "backup_dr": 1.5,
                           "brokerage_401k": 1.5, "legal": 1.5, "fleet": 0.3,
                           "freight_logistics": 0.2, "foodservice": 0.5},
    "healthcare": {"insurance_health": 1.5, "facilities": 1.5, "legal": 1.5,
                   "background_checks": 1.5, "fleet": 0.5},
    "retail": {"ecommerce": 2.0, "payments_processing": 2.0,
               "office_supplies": 1.5, "shipping_parcel": 1.5,
               "advertising": 1.5, "foodservice": 0.5, "fleet": 0.5},
    "manufacturing": {"freight_logistics": 2.0, "fleet": 2.0,
                      "office_supplies": 2.0, "erp": 1.5, "energy": 1.5,
                      "advertising": 0.3, "ecommerce": 0.5},
    "hospitality": {"foodservice": 2.0, "corporate_travel": 1.5,
                    "hotels": 0.5, "property": 1.0, "advertising": 1.5,
                    "freight_logistics": 0.3, "fleet": 0.5},
    "professional_services": {"corporate_travel": 1.5, "lms": 1.5,
                               "consulting": 0.5, "fleet": 0.3,
                               "freight_logistics": 0.2, "foodservice": 0.5},
}


def load_data():
    with open(os.path.join(DATA, "vendor_map.json")) as f:
        vendor_map = json.load(f)
    with open(os.path.join(DATA, "categories.json")) as f:
        categories = {c["id"]: c for c in json.load(f)["categories"]}
    return vendor_map["mappings"], categories


def coverage_report(mappings):
    by_status = defaultdict(int)
    by_sector = defaultdict(lambda: defaultdict(int))
    for m in mappings:
        by_status[m["status"]] += 1
        by_sector[m["sector"]][m["status"]] += 1
    return {
        "total_companies": len(mappings),
        "by_status": dict(by_status),
        "by_sector": {s: dict(v) for s, v in by_sector.items()},
    }


def category_vendors(mappings):
    """category id -> list of (ticker, name, product, note).

    Includes mapped offerings plus indirect offerings (which are
    employee-perks only by construction), so the perks category resolves.
    """
    out = defaultdict(list)
    for m in mappings:
        if m["status"] not in ("mapped", "indirect"):
            continue
        for o in m["offerings"]:
            if m["status"] == "indirect" and o["category"] != "employee_perks":
                continue
            out[o["category"]].append(
                {"ticker": m["ticker"], "vendor": m["name"],
                 "product": o["product"], "note": o.get("note", "")})
    return out


def estimate_spend(category, employees):
    spec = SPEND_MODEL[category]
    return round(spec["base"] * (employees / 200.0) ** spec["elasticity"])


def build_stack(mappings, categories, size_band, industry):
    if size_band not in SIZE_BANDS:
        raise ValueError("size_band must be one of %s" % list(SIZE_BANDS))
    if industry not in INDUSTRIES:
        raise ValueError("industry must be one of %s" % INDUSTRIES)
    employees = SIZE_BANDS[size_band]["employees"]
    band_idx = BAND_ORDER.index(size_band)
    weights = INDUSTRY_WEIGHTS.get(industry, {})
    vendors = category_vendors(mappings)
    usage = defaultdict(int)
    stack, uncovered = [], []
    for cat_id in sorted(SPEND_MODEL):
        spec = SPEND_MODEL[cat_id]
        if band_idx < spec["min_band"]:
            continue
        weight = weights.get(cat_id, 1.0)
        if weight <= 0:
            continue
        spend = round(estimate_spend(cat_id, employees) * weight)
        cands = sorted(vendors.get(cat_id, []),
                       key=lambda c: (usage[c["ticker"]], c["ticker"]))
        if not cands:
            uncovered.append(cat_id)
            continue
        pick = cands[0]
        usage[pick["ticker"]] += 1
        stack.append({
            "category": cat_id,
            "category_name": categories.get(cat_id, {}).get("name", cat_id),
            "ticker": pick["ticker"],
            "vendor": pick["vendor"],
            "product": pick["product"],
            "note": pick["note"],
            "weight": weight,
            "estimated_annual_spend_usd": spend,
        })
    total_spend = sum(s["estimated_annual_spend_usd"] for s in stack)
    vendor_spend = defaultdict(int)
    for s in stack:
        vendor_spend[s["ticker"]] += s["estimated_annual_spend_usd"]
    top_vendor, top_spend = max(vendor_spend.items(),
                                key=lambda kv: kv[1]) if vendor_spend else (None, 0)
    return {
        "size_band": size_band,
        "size_label": SIZE_BANDS[size_band]["label"],
        "industry": industry,
        "employees": employees,
        "stack": stack,
        "uncovered_categories": uncovered,
        "categories_covered": len(stack),
        "sp500_vendors_used": len(vendor_spend),
        "estimated_total_annual_spend_usd": total_spend,
        "estimated_sp500_revenue_directed_usd": total_spend,
        "top_vendor_concentration": {
            "ticker": top_vendor,
            "spend_usd": top_spend,
            "share_of_total": round(top_spend / total_spend, 4) if total_spend else 0.0,
        },
    }


def main():
    ap = argparse.ArgumentParser(description="S&P 500 Corporate Stack builder")
    ap.add_argument("--size", choices=list(SIZE_BANDS),
                    help="company size band")
    ap.add_argument("--industry", choices=INDUSTRIES,
                    help="company industry")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--coverage", action="store_true",
                    help="print the honest coverage report and exit")
    ap.add_argument("--emit-demo-data", action="store_true",
                    help="write demo/stack_data.js for all bands x industries")
    ap.add_argument("--out", default=os.path.join(HERE, "demo", "stack_data.js"))
    args = ap.parse_args()

    mappings, categories = load_data()

    if args.coverage:
        print(json.dumps(coverage_report(mappings), indent=2))
        return

    if args.emit_demo_data:
        data = {}
        for band in SIZE_BANDS:
            for ind in INDUSTRIES:
                data["%s__%s" % (band, ind)] = build_stack(
                    mappings, categories, band, ind)
        data["_meta"] = {
            "size_bands": SIZE_BANDS,
            "industries": INDUSTRIES,
            "coverage": coverage_report(mappings),
        }
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as f:
            f.write("window.SP500_STACK_DATA = ")
            json.dump(data, f)
            f.write(";\n")
        print("wrote %s" % args.out)
        return

    if not args.size or not args.industry:
        ap.error("--size and --industry are required (or use --coverage)")
    result = build_stack(mappings, categories, args.size, args.industry)
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return
    print("S&P 500 Corporate Stack")
    print("%s | %s" % (result["size_label"], result["industry"]))
    print("Categories covered: %d | S&P 500 vendors used: %d" % (
        result["categories_covered"], result["sp500_vendors_used"]))
    print("Est. annual spend: $%s" % f"{result['estimated_total_annual_spend_usd']:,}")
    print()
    for s in result["stack"]:
        print("  %-22s %-6s %-28s $%s" % (
            s["category_name"][:22], s["ticker"], s["product"][:28],
            f"{s['estimated_annual_spend_usd']:,}"))
    if result["uncovered_categories"]:
        print("\nUncovered (no S&P 500 vendor mapped): %s" % (
            ", ".join(result["uncovered_categories"])))


if __name__ == "__main__":
    main()