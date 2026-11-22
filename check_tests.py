import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scoring as sc

PASS = "✓ PASS"
FAIL = "✗ FAIL"

def check_test(name, result, expected_top3):
    ranked = result["ranked"]
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Warnings: {result['warnings']}")
    print("Ranked results:")
    for r in ranked:
        tied_str = " [TIED]" if r["tied"] else ""
        print(f"  Place {r['place']}: {r['crop']} score={r['total']} max={r['max_total']}{tied_str}")

    all_pass = True
    for i, (crop, exp_score, exp_tied) in enumerate(expected_top3):
        r = ranked[i]
        score_ok = r["total"] == exp_score
        tied_ok = r["tied"] == exp_tied
        crop_ok = r["crop"] == crop
        status = PASS if (score_ok and tied_ok and crop_ok) else FAIL
        if not (score_ok and tied_ok and crop_ok):
            all_pass = False
        print(f"  {status} pos={i+1}: crop={r['crop']} (expected={crop}) "
              f"score={r['total']} (expected={exp_score}) tied={r['tied']} (expected={exp_tied})")
    return all_pass

results_summary = []

# TEST 1: Athani | Black | Rabi | Soybean | No irrigation | Save water
r1 = sc.recommend_with_ties(
    lang="en", zone=sc.zone_for("Athani"), soil="black", season="rabi",
    last_crop="soybean", prev_crop=None, irrigation=False, priority="save_water"
)
p1 = check_test(
    "1: Athani / Black / Rabi / Soybean / No irrigation / Save water",
    r1,
    [("chickpea", 10, True), ("rabi_jowar", 10, True), ("wheat", 9, False)]
)
results_summary.append(("Test 1", p1))

# TEST 2: Belagavi | Black | Rabi | Maize | Irrigation YES | Safe harvest
r2 = sc.recommend_with_ties(
    lang="en", zone=sc.zone_for("Belagavi"), soil="black", season="rabi",
    last_crop="maize", prev_crop=None, irrigation=True, priority="safe_harvest"
)
p2 = check_test(
    "2: Belagavi / Black / Rabi / Maize / Irrigation YES / Safe harvest",
    r2,
    [("chickpea", 12, False), ("rabi_jowar", 10, True), ("wheat", 10, True)]
)
results_summary.append(("Test 2", p2))

# TEST 3: Khanapur | Black | Kharif | Wheat (prev: Soybean) | Irrigation YES | Improve soil
r3 = sc.recommend_with_ties(
    lang="en", zone=sc.zone_for("Khanapur"), soil="black", season="kharif",
    last_crop="wheat", prev_crop="soybean", irrigation=True, priority="soil_health"
)
p3 = check_test(
    "3: Khanapur / Black / Kharif / Wheat (prev=Soybean) / Irrigation YES / Improve soil",
    r3,
    [("green_gram", 10, True), ("black_gram", 10, True), ("soybean", 9, False)]
)
results_summary.append(("Test 3", p3))

# TEST 4: Athani | Black | Kharif | Fallow | No irrigation | Save water
r4 = sc.recommend_with_ties(
    lang="en", zone=sc.zone_for("Athani"), soil="black", season="kharif",
    last_crop="fallow", prev_crop=None, irrigation=False, priority="save_water"
)
p4 = check_test(
    "4: Athani / Black / Kharif / Fallow / No irrigation / Save water",
    r4,
    [("soybean", 8, True), ("green_gram", 8, True), ("black_gram", 8, True)]
)
results_summary.append(("Test 4", p4))

# SUMMARY
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
all_passed = True
for name, passed in results_summary:
    icon = "✓" if passed else "✗"
    print(f"  {icon} {name}: {'PASS' if passed else 'FAIL'}")
    if not passed:
        all_passed = False
print()
if all_passed:
    print("ALL PASS")
else:
    print("FAILURES DETECTED")
    sys.exit(1)
