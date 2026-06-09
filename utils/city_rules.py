"""
utils/city_rules.py
3-tier city coverage:
  Tier 1 — 4 metros with fully documented specific rules
  Tier 2 — 12 major cities with known municipal corporation rules
  Tier 3 — All other cities/towns/villages → SWM Rules 2026 national standard

SWM Rules 2026 mandate 4-bin segregation nationally — so national standard
is now legally correct for every city not in Tier 1 or 2.
"""

# ── Tier 1: Metro cities — fully specific rules ────────────────────────────────
TIER1 = {
    "Indore": {
        "organic":        {"bin_color": "green",    "bin_label": "Green Bin",        "action": "Daily IMC door-to-door collection. IMC helpline: 0731-2972001."},
        "dry_recyclable": {"bin_color": "blue",     "bin_label": "Blue Bin",         "action": "Daily IMC collection. Can also sell to kabadiwala for cash."},
        "hazardous":      {"bin_color": "red",      "bin_label": "Red Bin",          "action": "IMC separate hazardous collection. Call 0731-2972001 or use IMC app."},
        "sanitary":       {"bin_color": "yellow",   "bin_label": "Yellow Bin",       "action": "Wrap in newspaper. IMC yellow bin collection."},
        "e_waste":        {"bin_color": "black",    "bin_label": "Black Bin",        "action": "IMC e-waste drives quarterly. Check imcindore.org or call 0731-2972001."},
        "unknown":        {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Call IMC: 0731-2972001."},
    },
    "Delhi": {
        "organic":        {"bin_color": "green",    "bin_label": "Green Bin",        "action": "MCD door-to-door collection. Call MCD: 1800-11-0093."},
        "dry_recyclable": {"bin_color": "blue",     "bin_label": "Blue Bin",         "action": "MCD collection or sell to kabadiwala. Fine up to ₹10,000 for mixing."},
        "hazardous":      {"bin_color": "red",      "bin_label": "Red Bin",          "action": "MCD hazardous collection. Call 1800-11-0093."},
        "sanitary":       {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Wrap in newspaper. Keep separate from all waste. Never flush."},
        "e_waste":        {"bin_color": "separate", "bin_label": "E-Waste Drop-off", "action": "No black bin. Take to brand store (Samsung/Apple/Dell) or check dpcc.delhigovernment.gov.in."},
        "unknown":        {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Call MCD: 1800-11-0093."},
    },
    "Mumbai": {
        "organic":        {"bin_color": "green",    "bin_label": "Green Bin",        "action": "BMC door-to-door collection. BMC helpline: 1916."},
        "dry_recyclable": {"bin_color": "blue",     "bin_label": "Blue Bin",         "action": "BMC collection. Fine up to ₹15,000 for non-segregation."},
        "hazardous":      {"bin_color": "separate", "bin_label": "Hazardous Bag",    "action": "No red bin. Separate bag. Call BMC: 1916 for collection drives."},
        "sanitary":       {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Wrap securely. Never flush. BMC separate collection."},
        "e_waste":        {"bin_color": "separate", "bin_label": "E-Waste Drop-off", "action": "No black bin. Drop at brand store or check mpcb.gov.in for recyclers."},
        "unknown":        {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Call BMC: 1916."},
    },
    "Bengaluru": {
        "organic":        {"bin_color": "green",    "bin_label": "Green Bin",        "action": "BBMP collection. Apartments >50kg/day must compost on-site (OWC mandatory)."},
        "dry_recyclable": {"bin_color": "blue",     "bin_label": "Blue Bin",         "action": "BBMP collection. Charged ₹3/kg if not segregated. Call 080-22975555."},
        "hazardous":      {"bin_color": "red",      "bin_label": "Red Bin",          "action": "BBMP hazardous collection. Call 080-22975555."},
        "sanitary":       {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Wrap securely. BBMP separate collection. Never flush."},
        "e_waste":        {"bin_color": "separate", "bin_label": "E-Waste Drop-off", "action": "No black bin. Brand take-back (Samsung/Dell/HP) or check bbmp.gov.in."},
        "unknown":        {"bin_color": "separate", "bin_label": "Separate Bag",     "action": "Call BBMP: 080-22975555."},
    },
}

# ── Tier 2: Major cities — municipal corporation known, mostly SWM 2026 compliant ─
# These all follow green/blue/red/yellow standard under SWM Rules 2026
# with their own helpline numbers
TIER2 = {
    "Pune":        "020-25501104",
    "Hyderabad":   "040-21111111",
    "Chennai":     "044-25384519",
    "Kolkata":     "1800-345-2837",
    "Ahmedabad":   "079-25321811",
    "Jaipur":      "0141-2741242",
    "Lucknow":     "0522-2630180",
    "Surat":       "0261-2421919",
    "Kochi":       "0484-2823500",
    "Chandigarh":  "0172-2700432",
    "Nagpur":      "0712-2567021",
    "Bhopal":      "0755-2557891",
    "Patna":       "0612-2506080",
    "Vadodara":    "0265-2431201",
    "Coimbatore":  "0422-2399449",
}

# ── Tier 2 rules — SWM 2026 standard 4-bin with city helpline ──────────────────
def _tier2_rules(helpline: str) -> dict:
    return {
        "organic":        {"bin_color": "green",    "bin_label": "Green Bin",        "action": f"Green bin for wet/organic waste. Door-to-door collection by municipal corporation. Helpline: {helpline}."},
        "dry_recyclable": {"bin_color": "blue",     "bin_label": "Blue Bin",         "action": f"Blue bin for dry/recyclable waste. Keep clean and dry. Or sell to local kabadiwala. Helpline: {helpline}."},
        "hazardous":      {"bin_color": "red",      "bin_label": "Red Bin",          "action": f"Red bin for hazardous waste. Keep separate. For medicines — return to pharmacy. Helpline: {helpline}."},
        "sanitary":       {"bin_color": "yellow",   "bin_label": "Yellow Bin",       "action": f"Yellow bin for sanitary waste. Wrap in newspaper before disposal. Never flush. Helpline: {helpline}."},
        "e_waste":        {"bin_color": "separate", "bin_label": "E-Waste Drop-off", "action": f"Take to brand service centre (Samsung/Xiaomi/Dell accept free). Or call {helpline} for nearest e-waste drive."},
        "unknown":        {"bin_color": "separate", "bin_label": "Separate Bag",     "action": f"When unsure — keep separate. Call municipal helpline: {helpline}."},
    }

# ── Tier 3: National standard — SWM Rules 2026 ─────────────────────────────────
# Legally applies to ALL cities, towns, villages in India
TIER3_NATIONAL = {
    "organic":        {"bin_color": "green",    "bin_label": "Green Bin",           "action": "Green bin for wet/organic waste. No bin? Compost at home or bury in garden — it biodegrades safely."},
    "dry_recyclable": {"bin_color": "blue",     "bin_label": "Blue Bin",            "action": "Blue bin for dry/recyclable waste. No bin? Give to local kabadiwala or raddi collector for cash."},
    "hazardous":      {"bin_color": "red",      "bin_label": "Red Bin / Separate",  "action": "Red bin for hazardous waste. No bin? Collect separately. Take to nearest town municipal office. Medicines → return to any pharmacy."},
    "sanitary":       {"bin_color": "yellow",   "bin_label": "Yellow Bin / Bag",    "action": "Wrap in newspaper and seal tightly. Keep separate from ALL other waste. Never burn or flush — causes drain blockages."},
    "e_waste":        {"bin_color": "separate", "bin_label": "E-Waste Collection",  "action": "Take to nearest brand service centre (Samsung/Xiaomi/Dell all accept old devices free). Check cpcb.nic.in for nearest authorized recycler."},
    "unknown":        {"bin_color": "separate", "bin_label": "Separate Bag",        "action": "When unsure — keep separate from all bins. Contact your local gram panchayat or municipal office for guidance."},
}

# ── Build full city list for dropdown ──────────────────────────────────────────
SUPPORTED_CITIES = (
    sorted(TIER1.keys()) +
    sorted(TIER2.keys()) +
    ["Other (National Standard)"]
)

BIN_EMOJI = {
    "green": "🟢", "blue": "🔵", "red": "🔴",
    "black": "⚫", "yellow": "🟡", "separate": "⚠️",
}


def get_bin_guidance(category: str, city: str) -> dict:
    """Returns city-specific bin guidance for a waste category."""

    # Tier 1 — specific metro rules
    if city in TIER1:
        rules = TIER1[city]

    # Tier 2 — major cities with helpline
    elif city in TIER2:
        rules = _tier2_rules(TIER2[city])

    # Tier 3 — national standard for everyone else
    else:
        rules = TIER3_NATIONAL

    guidance = rules.get(category, rules["unknown"])
    guidance["display_label"] = f"{BIN_EMOJI[guidance['bin_color']]} {guidance['bin_label']}"
    return guidance