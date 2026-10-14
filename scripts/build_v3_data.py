#!/usr/bin/env python3
"""
v3 data build: three-tier relativity model.

1. Adds `consumer_channels` to every mapped vendor in data/vendor_map.json:
   the vendor's consumer-facing presence (B2C storefronts, subscriptions,
   consumer apps/services employees buy directly). Pure B2B vendors get an
   honest empty list; nothing is invented.
2. Adds `data/perk_categories.json`: the Consumer & Perks shelf for the 32
   indirect vendors, with ~12 perk categories and per-vendor assignments.
3. Tags each indirect vendor's record with its perk category assignments.

Reproducible: run from the repo root with `python3 scripts/build_v3_data.py`.
"""

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")

# ticker -> list of consumer-facing channels. Absent tickers default to [],
# which is the honest answer for pure B2B vendors.
CONSUMER_CHANNELS = {
    # --- Information Technology ---
    "AAPL": ["Apple Store retail and online", "iPhone, iPad, Mac for individuals",
             "App Store", "Apple Music"],
    "MSFT": ["Xbox consoles and Game Pass", "Surface devices",
             "Microsoft Store", "Windows for individuals"],
    "ADBE": ["Creative Cloud individual plans", "Adobe Acrobat",
             "Adobe Express"],
    "DELL": ["Dell.com consumer store", "Alienware gaming PCs"],
    "GDDY": ["GoDaddy.com domains and hosting for individuals"],
    "GEN": ["Norton antivirus", "LifeLock identity protection", "Avast"],
    "HPQ": ["HP.com consumer store", "HP printers and Instant Ink"],
    "INTU": ["TurboTax", "Credit Karma"],
    "NVDA": ["GeForce graphics cards", "Nvidia SHIELD"],
    # --- Communication Services ---
    "GOOGL": ["Google Pixel phones", "YouTube Premium", "Google One storage"],
    "META": ["Facebook", "Instagram", "WhatsApp", "Meta Quest headsets"],
    "T": ["AT&T wireless plans", "AT&T fiber internet"],
    "CHTR": ["Spectrum internet and TV"],
    "CMCSA": ["Xfinity internet and TV", "Peacock streaming"],
    "DIS": ["Disney+ streaming", "Disney Parks tickets and resorts", "Hulu"],
    "ECHO": ["Boost Mobile prepaid wireless", "DISH satellite TV"],
    "FOXA": ["Fox Nation streaming", "Tubi"],
    "LYV": ["Ticketmaster event tickets", "Live Nation concerts"],
    "NWSA": ["Wall Street Journal subscription", "Barron's"],
    "RDDT": ["Reddit Premium"],
    "SKYD": ["Paramount+ streaming"],
    "TKO": ["UFC pay-per-view and Fight Pass", "WWE events and Peacock"],
    "TMUS": ["T-Mobile wireless plans"],
    "VZ": ["Verizon wireless plans", "Verizon Fios"],
    # --- Consumer Discretionary ---
    "AMZN": ["Amazon.com", "Prime membership", "Whole Foods Market"],
    "ABNB": ["Airbnb stays booking"],
    "AZO": ["AutoZone retail stores"],
    "BBY": ["Best Buy stores"],
    "BKNG": ["Booking.com", "Priceline", "Kayak"],
    "CMG": ["Chipotle restaurants"],
    "DASH": ["DoorDash food delivery app"],
    "F": ["Ford vehicles at dealerships", "FordPass app"],
    "GM": ["Chevrolet, GMC, Cadillac vehicles", "OnStar"],
    "GPC": ["NAPA Auto Parts stores"],
    "HD": ["Home Depot stores"],
    "HLT": ["Hilton.com hotel booking", "Hilton Honors"],
    "LOW": ["Lowe's stores"],
    "LVS": ["Las Vegas Sands casino resorts"],
    "MAR": ["Marriott.com hotel booking", "Marriott Bonvoy"],
    "MGM": ["MGM Resorts properties", "BetMGM"],
    "ORLY": ["O'Reilly Auto Parts stores"],
    "SBUX": ["Starbucks stores and app"],
    "TSCO": ["Tractor Supply stores"],
    "TSLA": ["Tesla.com vehicle orders", "Tesla Supercharging"],
    "WYNN": ["Wynn Resorts properties"],
    # --- Consumer Staples ---
    "CLX": ["Clorox, Glad, Brita, Burt's Bees retail products"],
    "COST": ["Costco warehouse membership"],
    "KDP": ["Keurig brewers and K-Cups", "Dr Pepper"],
    "KMB": ["Kleenex", "Huggies", "Cottonelle"],
    "PG": ["Tide", "Pampers", "Gillette", "Dawn"],
    "TGT": ["Target stores", "Target Circle"],
    "TSN": ["Tyson", "Jimmy Dean", "Hillshire Farm", "Ball Park"],
    "WMT": ["Walmart stores", "Walmart+"],
    # --- Financials (consumer arms only; networks like Visa/Mastercard sell nothing direct) ---
    "AFL": ["Aflac supplemental insurance for individuals"],
    "ALL": ["Allstate auto and home insurance"],
    "AXP": ["American Express personal cards", "Amex Travel"],
    "AIG": ["AIG Travel Guard travel insurance"],
    "AMP": ["Ameriprise financial planning for individuals"],
    "AIZ": ["Assurant mobile device protection plans"],
    "BAC": ["Bank of America consumer banking", "Merrill Edge"],
    "BRK.B": ["GEICO auto insurance", "Berkshire consumer brands (Dairy Queen, Fruit of the Loom)"],
    "BLK": ["iShares ETFs for retail investors"],
    "XYZ": ["Cash App", "Square point of sale"],
    "CB": ["Chubb personal insurance for high-net-worth individuals"],
    "CINF": ["Cincinnati Insurance personal auto and home"],
    "C": ["Citi credit cards"],
    "CFG": ["Citizens Bank consumer banking"],
    "COIN": ["Coinbase retail crypto trading"],
    "SCHW": ["Charles Schwab retail brokerage"],
    "ERIE": ["Erie Insurance personal auto and home"],
    "FITB": ["Fifth Third Bank consumer banking"],
    "BEN": ["Franklin Templeton mutual funds for individuals"],
    "GL": ["Globe Life individual life insurance"],
    "GS": ["Marcus by Goldman Sachs savings"],
    "HIG": ["The Hartford personal auto and home insurance"],
    "HBAN": ["Huntington Bank consumer banking"],
    "IVZ": ["Invesco ETFs for individuals"],
    "JPM": ["Chase consumer banking and credit cards", "J.P. Morgan Wealth Management"],
    "KEY": ["KeyBank consumer banking"],
    "MET": ["MetLife individual life insurance and annuities"],
    "MS": ["E*TRADE from Morgan Stanley", "Morgan Stanley wealth management"],
    "MTB": ["M&T Bank consumer banking"],
    "NTRS": ["Northern Trust wealth management for individuals"],
    "PYPL": ["PayPal", "Venmo"],
    "PNC": ["PNC Bank consumer banking"],
    "PFG": ["Principal individual retirement and insurance"],
    "PGR": ["Progressive auto insurance", "Snapshot"],
    "PRU": ["Prudential individual life insurance and annuities"],
    "RF": ["Regions Bank consumer banking"],
    "SYF": ["Synchrony store credit cards"],
    "TROW": ["T. Rowe Price mutual funds for individuals"],
    "TRV": ["Travelers personal home and auto insurance"],
    "TFC": ["Truist consumer banking"],
    "USB": ["U.S. Bank consumer banking"],
    "WFC": ["Wells Fargo consumer banking"],
    # --- Health Care ---
    "CNC": ["Ambetter marketplace health plans"],
    "CI": ["Cigna individual health plans"],
    "CVS": ["CVS Pharmacy stores", "MinuteClinic", "Aetna individual plans"],
    "DGX": ["QuestDirect consumer lab testing"],
    "ELV": ["Elevance individual health plans"],
    "HUM": ["Humana Medicare Advantage plans"],
    "LH": ["Labcorp patient lab testing"],
    "UNH": ["UnitedHealthcare individual health plans"],
    # --- Industrials (consumer arms only) ---
    "MMM": ["Post-it", "Scotch", "Command strips"],
    "ALLE": ["Schlage residential locks at retail"],
    "CARR": ["Carrier residential HVAC through dealers"],
    "DAL": ["Delta.com flight booking", "SkyMiles"],
    "DE": ["John Deere lawn and garden equipment at dealers"],
    "FDX": ["FedEx.com shipping for individuals"],
    "GNRC": ["Generac home standby generators"],
    "LUV": ["Southwest.com flight booking", "Rapid Rewards"],
    "PNR": ["Pentair pool equipment through dealers"],
    "ROL": ["Orkin residential pest control"],
    "SNA": ["Snap-on tools"],
    "SWK": ["DeWalt tools", "Craftsman tools", "Stanley tools"],
    "TT": ["Trane residential HVAC through dealers"],
    "UAL": ["United.com flight booking", "MileagePlus"],
    "UBER": ["Uber rides", "Uber Eats"],
    "UPS": ["UPS.com shipping for individuals"],
    # --- Utilities (residential service is genuinely consumer-facing) ---
    "LNT": ["Alliant Energy residential electric and gas service"],
    "AEE": ["Ameren residential electric and gas service"],
    "AEP": ["American Electric Power residential service"],
    "ATO": ["Atmos Energy residential natural gas service"],
    "AWK": ["American Water residential water service"],
    "CNP": ["CenterPoint Energy residential service"],
    "CMS": ["Consumers Energy residential service"],
    "ED": ["Con Edison residential electric and gas service"],
    "CEG": ["Constellation residential energy plans"],
    "D": ["Dominion Energy residential service"],
    "DTE": ["DTE Energy residential service"],
    "DUK": ["Duke Energy residential service"],
    "EIX": ["Southern California Edison residential service"],
    "ETR": ["Entergy residential service"],
    "EVRG": ["Evergy residential service"],
    "ES": ["Eversource residential service"],
    "EXC": ["Exelon utility residential service (ComEd, PECO)"],
    "FE": ["FirstEnergy residential service"],
    "NEE": ["FPL residential electric service"],
    "NI": ["NiSource residential gas service"],
    "NRG": ["NRG home energy plans"],
    "PCG": ["PG&E residential electric and gas service"],
    "PNW": ["Arizona Public Service residential service"],
    "PPL": ["PPL residential electric service"],
    "PEG": ["PSE&G residential service"],
    "SO": ["Southern Company utility residential service"],
    "SRE": ["Sempra utility residential service (SoCalGas, SDG&E)"],
    "VST": ["TXU Energy residential plans"],
    "WEC": ["WEC Energy residential service"],
    "XEL": ["Xcel Energy residential service"],
    # --- Energy (retail fuel) ---
    "CVX": ["Chevron and Texaco gas stations"],
    "XOM": ["Exxon and Mobil gas stations"],
    "PSX": ["Phillips 66, 76, and Conoco gas stations"],
    "VLO": ["Valero gas stations"],
    # --- Materials ---
    "PPG": ["Olympic and Glidden paint at retail"],
    "SHW": ["Sherwin-Williams paint stores"],
    # --- Real Estate (consumer-facing only) ---
    "EXR": ["Extra Space Storage self-storage units"],
    "PSA": ["Public Storage self-storage units"],
}

# ~12 perk categories for the Consumer & Perks shelf (the 32 indirect vendors).
# spend_per_employee: order-of-magnitude annual USD per employee.
PERK_CATEGORIES = [
    {"id": "cruises", "name": "Cruises",
     "description": "Corporate cruise events and employee cruise discounts",
     "spend_per_employee": 40},
    {"id": "dining", "name": "Dining",
     "description": "Restaurant catering, group meals, and meal perks",
     "spend_per_employee": 120},
    {"id": "streaming", "name": "Streaming",
     "description": "Video streaming subscriptions as an employee perk",
     "spend_per_employee": 60},
    {"id": "apparel", "name": "Apparel",
     "description": "Branded apparel and clothing discounts",
     "spend_per_employee": 80},
    {"id": "footwear", "name": "Footwear",
     "description": "Footwear programs and discounts",
     "spend_per_employee": 40},
    {"id": "beauty", "name": "Beauty & Personal Care",
     "description": "Beauty and personal care product perks",
     "spend_per_employee": 30},
    {"id": "home_goods", "name": "Home Goods",
     "description": "Home furnishings and decor discounts",
     "spend_per_employee": 40},
    {"id": "beverages", "name": "Beverages",
     "description": "Office and break-room beverage programs",
     "spend_per_employee": 50},
    {"id": "snacks", "name": "Snacks & Confectionery",
     "description": "Snack programs and confectionery perks",
     "spend_per_employee": 60},
    {"id": "packaged_foods", "name": "Packaged Foods",
     "description": "Pantry staples and packaged food programs",
     "spend_per_employee": 40},
    {"id": "toys_games", "name": "Toys & Games",
     "description": "Family toys and games perks",
     "spend_per_employee": 15},
    {"id": "wearables", "name": "Wearables & Electronics",
     "description": "Wearable tech and electronics discounts",
     "spend_per_employee": 25},
]

# ticker -> list of {perk_category, perk}: the specific perk offering.
INDIRECT_PERKS = {
    "CCL": [{"perk_category": "cruises",
             "perk": "Carnival corporate cruise events and employee cruise discounts"}],
    "NCLH": [{"perk_category": "cruises",
              "perk": "Norwegian corporate cruise events and employee cruise discounts"}],
    "RCL": [{"perk_category": "cruises",
             "perk": "Royal Caribbean corporate cruise events and employee cruise discounts"}],
    "DRI": [{"perk_category": "dining",
             "perk": "Darden restaurant catering (Olive Garden, LongHorn)"}],
    "MCD": [{"perk_category": "dining",
             "perk": "McDonald's group meals and catering"}],
    "YUM": [{"perk_category": "dining",
             "perk": "Yum! Brands catering (KFC, Pizza Hut, Taco Bell)"}],
    "DPZ": [{"perk_category": "dining",
             "perk": "Domino's group pizza orders"}],
    "NFLX": [{"perk_category": "streaming",
              "perk": "Netflix subscription as an employee perk"}],
    "NKE": [{"perk_category": "apparel",
             "perk": "Nike corporate apparel programs"},
            {"perk_category": "footwear",
             "perk": "Nike footwear discounts"}],
    "LULU": [{"perk_category": "apparel",
              "perk": "Lululemon corporate apparel programs"}],
    "RL": [{"perk_category": "apparel",
            "perk": "Ralph Lauren corporate apparel"}],
    "TPR": [{"perk_category": "apparel",
             "perk": "Tapestry brand corporate gifting (Coach, Kate Spade)"}],
    "ROST": [{"perk_category": "apparel",
              "perk": "Ross Stores employee discount programs"},
             {"perk_category": "home_goods",
              "perk": "Ross home goods discounts"}],
    "TJX": [{"perk_category": "apparel",
             "perk": "TJX employee discount programs (TJ Maxx, Marshalls)"},
            {"perk_category": "home_goods",
             "perk": "HomeGoods discounts"}],
    "DECK": [{"perk_category": "footwear",
              "perk": "Deckers footwear programs (UGG, Hoka)"}],
    "EL": [{"perk_category": "beauty",
            "perk": "Estee Lauder corporate beauty programs"}],
    "ULTA": [{"perk_category": "beauty",
              "perk": "Ulta Beauty employee discount programs"}],
    "KVUE": [{"perk_category": "beauty",
              "perk": "Kenvue personal care programs (Neutrogena, Aveeno)"}],
    "CHD": [{"perk_category": "beauty",
             "perk": "Church & Dwight personal care (Arm & Hammer)"}],
    "WSM": [{"perk_category": "home_goods",
             "perk": "Williams-Sonoma corporate home furnishing programs"}],
    "KO": [{"perk_category": "beverages",
            "perk": "Coca-Cola office beverage programs"}],
    "PEP": [{"perk_category": "beverages",
             "perk": "PepsiCo office beverage programs"},
            {"perk_category": "snacks",
             "perk": "Frito-Lay snack programs"}],
    "MNST": [{"perk_category": "beverages",
              "perk": "Monster Energy office beverage programs"}],
    "MDLZ": [{"perk_category": "snacks",
              "perk": "Mondelez snack programs (Oreo, Cadbury)"}],
    "HSY": [{"perk_category": "snacks",
             "perk": "Hershey confectionery programs"}],
    "GIS": [{"perk_category": "packaged_foods",
             "perk": "General Mills pantry programs (Cheerios, Nature Valley)"}],
    "KHC": [{"perk_category": "packaged_foods",
             "perk": "Kraft Heinz pantry programs"}],
    "HRL": [{"perk_category": "packaged_foods",
             "perk": "Hormel foods programs (Skippy, Spam)"}],
    "SJM": [{"perk_category": "packaged_foods",
             "perk": "Smucker coffee and pantry programs (Folgers)"}],
    "MKC": [{"perk_category": "packaged_foods",
             "perk": "McCormick spice programs"}],
    "HAS": [{"perk_category": "toys_games",
             "perk": "Hasbro family toys and games programs"}],
    "GRMN": [{"perk_category": "wearables",
              "perk": "Garmin wearable corporate wellness programs"}],
}


def main():
    with open(os.path.join(DATA, "vendor_map.json")) as f:
        vendor_map = json.load(f)
    mappings = vendor_map["mappings"]

    n_mapped_cc = 0
    for m in mappings:
        if m["status"] == "mapped":
            channels = CONSUMER_CHANNELS.get(m["ticker"], [])
            m["consumer_channels"] = channels
            if channels:
                n_mapped_cc += 1
        elif m["status"] == "indirect":
            perks = INDIRECT_PERKS.get(m["ticker"], [])
            m["perk_assignments"] = perks

    # Every indirect vendor must be assigned; fail loudly otherwise.
    unassigned = [m["ticker"] for m in mappings
                  if m["status"] == "indirect" and not m.get("perk_assignments")]
    if unassigned:
        raise SystemExit("indirect vendors missing perk assignments: %s"
                         % unassigned)

    with open(os.path.join(DATA, "vendor_map.json"), "w") as f:
        json.dump(vendor_map, f, indent=2)
        f.write("\n")

    with open(os.path.join(DATA, "perk_categories.json"), "w") as f:
        json.dump({"categories": PERK_CATEGORIES}, f, indent=2)
        f.write("\n")

    n_mapped = sum(1 for m in mappings if m["status"] == "mapped")
    n_indirect = sum(1 for m in mappings if m["status"] == "indirect")
    n_unmapped = sum(1 for m in mappings if m["status"] == "unmapped")
    print("mapped=%d indirect=%d unmapped=%d total=%d" % (
        n_mapped, n_indirect, n_unmapped, len(mappings)))
    print("mapped vendors with consumer channels: %d/%d" % (n_mapped_cc, n_mapped))
    print("perk categories: %d" % len(PERK_CATEGORIES))


if __name__ == "__main__":
    main()
