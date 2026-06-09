"""
tests/test_pipeline.py
Structured accuracy test for WasteWise India.
Tests text-based classification (no image needed — runs without camera).
Run: python -m tests.test_pipeline
"""

from rag.chain import run_pipeline

# ── Test cases: (description, expected_category, expected_bin_indore) ─────────
TEST_CASES = [
    # Organic
    ("banana peel",                     "organic",          "Green Bin"),
    ("leftover rice and curry",         "organic",          "Green Bin"),
    ("vegetable cuttings",              "organic",          "Green Bin"),
    ("used tea leaves",                 "organic",          "Green Bin"),
    ("agarbatti ash",                   "organic",          "Green Bin"),

    # Dry Recyclable
    ("plastic water bottle",            "dry_recyclable",   "Blue Bin"),
    ("newspaper",                       "dry_recyclable",   "Blue Bin"),
    ("cardboard box",                   "dry_recyclable",   "Blue Bin"),
    ("glass bottle",                    "dry_recyclable",   "Blue Bin"),
    ("aluminium can",                   "dry_recyclable",   "Blue Bin"),

    # Hazardous
    ("paint can with leftover paint",   "hazardous",        "Red Bin"),
    ("expired medicines",               "hazardous",        "Red Bin"),
    ("mosquito repellent spray can",    "hazardous",        "Red Bin"),
    ("bleach cleaning bottle",          "hazardous",        "Red Bin"),

    # E-waste
    ("old mobile phone",                "e_waste",          "Black Bin"),
    ("AA battery",                      "e_waste",          "Black Bin"),
    ("broken laptop charger",           "e_waste",          "Black Bin"),
    ("CFL bulb",                        "e_waste",          "Black Bin"),

    # Sanitary
    ("used sanitary pad",               "sanitary",         "Yellow Bin"),
    ("used diaper",                     "sanitary",         "Yellow Bin"),

    # Tricky / confusing items
    ("medicine blister pack",           "hazardous",        "Red Bin"),
    ("greasy pizza box",                "organic",          "Green Bin"),
    ("bubble wrap",                     "dry_recyclable",   "Blue Bin"),
    ("chip packet foil wrapper",        "dry_recyclable",   "Blue Bin"),
    ("old torn clothes",                "dry_recyclable",   None),   # acceptable — no textile bin exists
]


def run_tests():
    total    = len(TEST_CASES)
    cat_pass = 0
    bin_pass = 0
    failures = []

    print(f"\n{'='*62}")
    print(f"  WasteWise India — Accuracy Test ({total} items | city=Indore)")
    print(f"{'='*62}\n")

    for description, expected_cat, expected_bin in TEST_CASES:
        result, _ = run_pipeline(text_input=description, city="Indore")

        got_cat = result.get("category", "unknown")
        got_bin = result.get("bin_label", "")

        cat_ok = got_cat == expected_cat
        bin_ok = expected_bin is None or expected_bin in got_bin

        if cat_ok: cat_pass += 1
        if bin_ok: bin_pass += 1

        status = "✅" if (cat_ok and bin_ok) else "❌"
        print(f"{status}  {description:<35} | {expected_cat:<15} → {got_cat}")

        if not (cat_ok and bin_ok):
            failures.append({
                "item":         description,
                "expected_cat": expected_cat,
                "got_cat":      got_cat,
                "expected_bin": expected_bin,
                "got_bin":      got_bin,
            })

    print(f"\n{'='*62}")
    print(f"  Category accuracy : {cat_pass}/{total} = {cat_pass/total*100:.0f}%")
    print(f"  Bin accuracy      : {bin_pass}/{total} = {bin_pass/total*100:.0f}%")
    print(f"{'='*62}")

    if failures:
        print(f"\n❌ Failed ({len(failures)} items):")
        for f in failures:
            print(f"  • {f['item']}")
            print(f"    category : expected={f['expected_cat']}  got={f['got_cat']}")
            print(f"    bin      : expected={f['expected_bin']}  got={f['got_bin']}")
    else:
        print("\n🎉 All tests passed!")

    print()


if __name__ == "__main__":
    run_tests()