import os
import re
from typing import NamedTuple, Optional, Dict
import pandas as pd


class RotationScore(NamedTuple):
    points: int
    why: str
    confidence: str


class PartScore(NamedTuple):
    points: int
    why: str


def _level(crop, water_overrides=None):
    if water_overrides and crop in water_overrides:
        return water_overrides[crop]
    return crop_info[crop]["water_level"]

# =====================================================================
# PART 1: SETTINGS. Every number the tool uses lives here, nowhere else.
# =====================================================================
SETTINGS = {
    # Zone labels come from climate_zones.csv (your NASA analysis)
    "zones": {
        "Belagavi": {"rain_supply": "high", "dry_spell_risk": "low",
                     "waterlogging_risk": "medium", "rabi_stored_moisture": "high"},
        "Khanapur": {"rain_supply": "high", "dry_spell_risk": "low",
                     "waterlogging_risk": "high", "rabi_stored_moisture": "high"},
        "Athani":   {"rain_supply": "low", "dry_spell_risk": "high",
                     "waterlogging_risk": "low", "rabi_stored_moisture": "low"},
    },
    "level": {"low": 0, "medium": 1, "high": 2},

    # Points for rotation fit (out of 3)
    "rotation_points": {"sourced_confirmed": 3, "sourced_not_sure": 2,
                        "legume_cereal_change": 2, "same_type_change": 1,
                        "no_data": 1, "repeat": 0},
    # Points for soil fit (out of 2)
    "soil_points": {"evidence": 2, "no_evidence": 1},
    # Points for water use (out of 2): less water = more points
    "water_use_points": {"low": 2, "medium": 1, "high": 0},

    # Climate fit starts at this and loses points for problems
    "climate_start": 3,
    "irrigation_reduces_stress_penalty_by": 1,
    "waterlogging_penalty": 1,
    "waterlogging_sensitive": ["soybean", "maize"],

    # What the farmer cares about changes how much each part counts
    "priority_weights": {
        "balanced":     {"rotation": 1, "soil": 1, "climate": 1, "water_use": 1},
        "soil_health":  {"rotation": 2, "soil": 1, "climate": 1, "water_use": 1},
        "save_water":   {"rotation": 1, "soil": 1, "climate": 1, "water_use": 3},
        "safe_harvest": {"rotation": 1, "soil": 1, "climate": 2, "water_use": 1},
    },
}
S = SETTINGS

MAX_PART_POINTS = {
    "rotation": max(SETTINGS["rotation_points"].values()),
    "soil": max(SETTINGS["soil_points"].values()),
    "climate": SETTINGS["climate_start"],
    "water_use": max(SETTINGS["water_use_points"].values()),
}

TALUK_KN = {
    "Belagavi": "ಬೆಳಗಾವಿ", "Chikkodi": "ಚಿಕ್ಕೋಡಿ", "Hukkeri": "ಹುಕ್ಕೇರಿ",
    "Bailhongal": "ಬೈಲಹೊಂಗಲ", "Raibag": "ರಾಯಭಾಗ", "Gokak": "ಗೋಕಾಕ",
    "Athani": "ಅಥಣಿ", "Ramdurg": "ರಾಮದುರ್ಗ", "Saundatti": "ಸವದತ್ತಿ",
    "Khanapur": "ಖಾನಾಪುರ",
}
SOIL_KN = {"black": "ಕಪ್ಪು ಮಣ್ಣು", "red": "ಕೆಂಪು ಮಣ್ಣು", "sandy": "ಮರಳು ಮಣ್ಣು"}
SEASON = {"kharif": ("Kharif (monsoon)", "ಮುಂಗಾರು"), "rabi": ("Rabi (winter)", "ಹಿಂಗಾರು")}
PRIORITY = {
    "soil_health": ("Improve my soil", "ನನ್ನ ಮಣ್ಣು ಸುಧಾರಿಸಬೇಕು"),
    "save_water": ("Save water", "ನೀರು ಉಳಿಸಬೇಕು"),
    "safe_harvest": ("A safe harvest", "ಸುರಕ್ಷಿತ ಫಸಲು ಬೇಕು"),
}
# NASA POWER 1981-2025 facts per zone (model estimate). Recalculated from the yearly files.
ZONE_FACTS = {"Athani": 84, "Belagavi": 27, "Khanapur": 22}

# Official agro-climatic zones (CRIDA 2011) mapped to our three NASA points
TALUK_TO_ZONE = {
    "Belagavi": "Belagavi", "Chikkodi": "Belagavi", "Hukkeri": "Belagavi", "Bailhongal": "Belagavi",
    "Raibag": "Athani", "Gokak": "Athani", "Athani": "Athani", "Ramdurg": "Athani", "Saundatti": "Athani",
    "Khanapur": "Khanapur",
}


def zone_for(taluk):
    if taluk not in TALUK_TO_ZONE:
        raise ValueError(f"taluk must be one of {list(TALUK_TO_ZONE)}")
    return TALUK_TO_ZONE[taluk]


# =====================================================================
# PART 1b: WORDS IN ENGLISH AND KANNADA (ask a Kannada speaker to check)
# =====================================================================
WORDS = {
    "en": {
        "levels": {"low": "low", "medium": "medium", "high": "high"},
        "soils": {"black": "black", "red": "red", "sandy": "sandy"},
        "zones": {"Belagavi": "Belagavi", "Khanapur": "Khanapur", "Athani": "Athani"},
        "text": {
            "same_third": "same crop for the third season in a row, avoid",
            "same_again": "same crop again",
            "source_tag": " (source {src})",
            "legume_cereal": "legume and cereal alternate (general rule, no sourced pair)",
            "same_type": "different crop of the same type (no sourced pair)",
            "no_rot_data": "no sourced rotation data for the last crop",
            "soil_yes": "sourced evidence for {soil} soil",
            "soil_no": "no sourced evidence for {soil} soil",
            "stress_kharif": "{zone} monsoon stress: dry spells {dry}, rain supply {supply}",
            "stress_rabi": "{zone} stored soil moisture for rabi: {moist}",
            "irrigation": "irrigation reduces the water stress",
            "waterlog": "waterlogging risk is high here and this crop is sensitive to it",
            "water_use": "{level} water need",
            "warn_soil": "Little or no sourced rotation evidence for {soil} soil. Treat this as a rough guide.",
            "warn_other": "No sourced rotation data for {crop}. Rotation scores use no data.",
            "warn_water": "The water need of {crop} is not confirmed by an expert yet.",
            "strat_usual": "Your usual choice",
            "strat_alt": "Alternative {n}",
            "legume_crop": "legume crop",
            "root_depth": "root depth about {depth} m",
            "gap_no_data": "no yield, price or pest data in this tool",
            "gap_water": "water need not confirmed by an expert",
            "gap_rot": "no sourced rotation pair for this last crop and soil",
            "gap_soil": "no sourced evidence for this soil",
            "risk_review": "needs local review by the farmer and an agriculture expert",
            "ev_none": "no sourced rotation pair",
            "str_confirmed": "confirmed",
            "str_not_sure": "not_sure",
            "str_general": "general rule",
            "str_none": "none",
        },
    },
    "kn": {
        "levels": {"low": "ಕಡಿಮೆ", "medium": "ಮಧ್ಯಮ", "high": "ಹೆಚ್ಚು"},
        "soils": {"black": "ಕಪ್ಪು", "red": "ಕೆಂಪು", "sandy": "ಮರಳು"},
        "zones": {"Belagavi": "ಬೆಳಗಾವಿ", "Khanapur": "ಖಾನಾಪುರ", "Athani": "ಅಥಣಿ"},
        "text": {
            "same_third": "ಸತತ ಮೂರನೇ ಹಂಗಾಮಿನಲ್ಲೂ ಅದೇ ಬೆಳೆ, ಬೇಡ",
            "same_again": "ಅದೇ ಬೆಳೆ ಮತ್ತೆ",
            "source_tag": " (ಆಧಾರ: {src})",
            "legume_cereal": "ಬೇಳೆಕಾಳು ಮತ್ತು ಧಾನ್ಯ ಬೆಳೆಗಳನ್ನು ಬದಲಿಸಿ ಬೆಳೆಯುವುದು (ಸಾಮಾನ್ಯ ನಿಯಮ, ಆಧಾರಿತ ಜೋಡಿ ಇಲ್ಲ)",
            "same_type": "ಅದೇ ಬಗೆಯ ಬೇರೆ ಬೆಳೆ (ಆಧಾರಿತ ಜೋಡಿ ಇಲ್ಲ)",
            "no_rot_data": "ಹಿಂದಿನ ಬೆಳೆಗೆ ಆಧಾರಿತ ಬೆಳೆ ಪರ್ಯಾಯ ಮಾಹಿತಿ ಇಲ್ಲ",
            "soil_yes": "{soil} ಮಣ್ಣಿಗೆ ಆಧಾರಿತ ಮಾಹಿತಿ ಇದೆ",
            "soil_no": "{soil} ಮಣ್ಣಿಗೆ ಆಧಾರಿತ ಮಾಹಿತಿ ಇಲ್ಲ",
            "stress_kharif": "{zone}: ಮುಂಗಾರು ಒತ್ತಡ. ಒಣ ಅವಧಿಯ ಅಪಾಯ {dry}, ಮಳೆ ಲಭ್ಯತೆ {supply}",
            "stress_rabi": "{zone}: ಹಿಂಗಾರಿಗೆ ಮಣ್ಣಿನ ತೇವಾಂಶ {moist}",
            "irrigation": "ನೀರಾವರಿಯಿಂದ ನೀರಿನ ಒತ್ತಡ ಕಡಿಮೆಯಾಗುತ್ತದೆ",
            "waterlog": "ಇಲ್ಲಿ ನೀರು ನಿಲ್ಲುವ ಅಪಾಯ ಹೆಚ್ಚು, ಈ ಬೆಳೆ ಅದಕ್ಕೆ ಸೂಕ್ಷ್ಮ",
            "water_use": "ನೀರಿನ ಅವಶ್ಯಕತೆ {level}",
            "warn_soil": "{soil} ಮಣ್ಣಿಗೆ ಆಧಾರಿತ ಬೆಳೆ ಪರ್ಯಾಯ ಮಾಹಿತಿ ಕಡಿಮೆ ಅಥವಾ ಇಲ್ಲ. ಇದನ್ನು ಸ್ಥೂಲ ಮಾರ್ಗದರ್ಶನ ಎಂದು ಪರಿಗಣಿಸಿ.",
            "warn_other": "{crop} ಬೆಳೆಗೆ ಆಧಾರಿತ ಪರ್ಯಾಯ ಮಾಹಿತಿ ಇಲ್ಲ. ಬೆಳೆ ಪರ್ಯಾಯದ ಅಂಕಗಳನ್ನು ಮಾಹಿತಿ ಇಲ್ಲದೆ ಲೆಕ್ಕಹಾಕಲಾಗಿದೆ.",
            "warn_water": "{crop} ಬೆಳೆಯ ನೀರಿನ ಅವಶ್ಯಕತೆಯನ್ನು ತಜ್ಞರು ಇನ್ನೂ ದೃಢಪಡಿಸಿಲ್ಲ.",
            "strat_usual": "ನಿಮ್ಮ ಸಾಮಾನ್ಯ ಆಯ್ಕೆ",
            "strat_alt": "ಪರ್ಯಾಯ {n}",
            "legume_crop": "ಬೇಳೆಕಾಳು ಬೆಳೆ",
            "root_depth": "ಬೇರಿನ ಆಳ ಸುಮಾರು {depth} ಮೀಟರ್",
            "gap_no_data": "ಈ ಸಾಧನದಲ್ಲಿ ಇಳುವರಿ, ಬೆಲೆ ಅಥವಾ ಕೀಟಬಾಧೆಯ ಮಾಹಿತಿ ಇಲ್ಲ",
            "gap_water": "ನೀರಿನ ಅವಶ್ಯಕತೆಯನ್ನು ತಜ್ಞರು ಇನ್ನೂ ದೃಢಪಡಿಸಿಲ್ಲ",
            "gap_rot": "ಹಿಂದಿನ ಬೆಳೆ ಮತ್ತು ಮಣ್ಣಿಗೆ ಆಧಾರಿತ ಜೋಡಿ ಇಲ್ಲ",
            "gap_soil": "ಈ ಮಣ್ಣಿಗೆ ಆಧಾರಿತ ಮಾಹಿತಿ ಇಲ್ಲ",
            "risk_review": "ರೈತರು ಮತ್ತು ಕೃಷಿ ತಜ್ಞರಿಂದ ಸ್ಥಳೀಯ ಪರಿಶೀಲನೆ ಅಗತ್ಯ",
            "ev_none": "ಆಧಾರಿತ ಜೋಡಿ ಇಲ್ಲ",
            "str_confirmed": "ದೃಢಪಟ್ಟಿದೆ",
            "str_not_sure": "ಖಚಿತವಿಲ್ಲ",
            "str_general": "ಸಾಮಾನ್ಯ ನಿಯಮ",
            "str_none": "ಮಾಹಿತಿ ಇಲ್ಲ",
        },
    },
}

# Kannada version of the evidence line for each sourced rotation pair
EVIDENCE_KN = {
    ("maize", "chickpea"): "ಯುಎಎಸ್ ಧಾರವಾಡದ ಯೋಜನೆಯಲ್ಲಿ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಸಾಮಾನ್ಯವಾಗಿ ಅನುಸರಿಸುವ ಬೆಳೆ ಪದ್ಧತಿ ಎಂದು ಪಟ್ಟಿ ಮಾಡಲಾಗಿದೆ. 2014ರ ಯುಎಎಸ್ ಸಂಶೋಧನಾ ಪ್ರಬಂಧದ ಪರಿಚಯ ಭಾಗದಲ್ಲಿ ಉತ್ತರ ಕರ್ನಾಟಕದ ನೀರಾವರಿ ಪ್ರದೇಶಗಳಿಗೆ ಇದು ಸೂಕ್ತವಾದ ಬೆಳೆ ಪದ್ಧತಿ ಎಂದು ಹೇಳಲಾಗಿದೆ",
    ("soybean", "rabi_jowar"): "ಯುಎಎಸ್ ಧಾರವಾಡದ ಯೋಜನೆಯಲ್ಲಿ ಮಧ್ಯಮ ಆಳದ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಮಳೆಯಾಶ್ರಿತವಾಗಿ ಸಾಮಾನ್ಯವಾಗಿ ಅನುಸರಿಸುವ ಬೆಳೆ ಪದ್ಧತಿ ಎಂದು ಪಟ್ಟಿ ಮಾಡಲಾಗಿದೆ",
    ("green_gram", "rabi_jowar"): "ಯುಎಎಸ್ ಧಾರವಾಡದ ಯೋಜನೆಯಲ್ಲಿ ಮಧ್ಯಮ ಆಳದ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಸಾಮಾನ್ಯವಾಗಿ ಅನುಸರಿಸುವ ಬೆಳೆ ಪದ್ಧತಿ ಎಂದು ಪಟ್ಟಿ ಮಾಡಲಾಗಿದೆ",
    ("green_gram", "wheat"): "ಯುಎಎಸ್ ಧಾರವಾಡದ ಯೋಜನೆಯಲ್ಲಿ ಮಧ್ಯಮ ಆಳದ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಹೆಸರು ನಂತರ ಗೋಧಿ ಬೆಳೆಯುವ ಬೆಳೆ ಪದ್ಧತಿ ಎಂದು ಪಟ್ಟಿ ಮಾಡಲಾಗಿದೆ",
    ("black_gram", "rabi_jowar"): "ಸಾಧ್ಯವಾದಲ್ಲಿ, ಹಿಂಗಾರು ಜೋಳ ಬೆಳೆಯುವ ಮೊದಲು ಉದ್ದಿನಂತಹ ಬೇಳೆ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯುವಂತೆ ಐಸಿಎಆರ್ ಜೋಳದ ಮಾರ್ಗದರ್ಶಿಯಲ್ಲಿ ಸೂಚಿಸಲಾಗಿದೆ",
    ("soybean", "chickpea"): "ಯುಎಎಸ್ ಧಾರವಾಡದಲ್ಲಿ 2005–07ರಲ್ಲಿ ನಡೆಸಿದ ಪ್ರಯೋಗದಲ್ಲಿ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಸುಧಾರಿಸಿರುವುದು ಕಂಡುಬಂದಿದೆ. ರಾಹುರಿಯಲ್ಲಿಯೂ ಸೀಮಿತ ನೀರಾವರಿ ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ಈ ಪದ್ಧತಿಯನ್ನು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ. ಆದರೆ, ಇಳುವರಿಯಲ್ಲಿ ಇದೇ ಅತ್ಯುತ್ತಮ ಪದ್ಧತಿ ಎಂದು ಸ್ಪಷ್ಟವಾಗಿ ಸಾಬೀತಾಗಿಲ್ಲ",
}

# =====================================================================
# PART 2: LOAD THE TABLES
# =====================================================================
_DIR = os.path.dirname(os.path.abspath(__file__))
crops = pd.read_csv(os.path.join(_DIR, "crops.csv"), encoding="utf-8-sig")
rotations = pd.read_csv(os.path.join(_DIR, "rotations.csv"), encoding="utf-8-sig")
others = pd.read_csv(os.path.join(_DIR, "other_previous_crops.csv"), encoding="utf-8-sig")
crop_info = crops.set_index("crop").to_dict("index")
other_info = others.set_index("crop").to_dict("index")


def say(lang, key, **kw):
    return WORDS[lang]["text"][key].format(**kw)


def crop_word(lang, crop):
    if lang == "en":
        return crop.replace("_", " ")
    info = crop_info.get(crop) or other_info.get(crop)
    return info["name_kn"]


def _build_soil_evidence():
    lookup = {}
    soils = list(WORDS["en"]["soils"])
    all_crops = list(crop_info) + list(other_info)
    for s in soils:
        rows = rotations[rotations["soil"] == s]
        in_rot_crops = set(rows["previous_crop"]) | set(rows["next_crop"])
        for c in all_crops:
            in_rotations = c in in_rot_crops
            notes = str(crop_info[c]["soil_notes"]).lower() if c in crop_info else ""
            in_notes = re.search(rf"\b{s}\b", notes) is not None
            lookup[(c, s)] = in_rotations or in_notes
    return lookup

_SOIL_EVIDENCE_LOOKUP = _build_soil_evidence()


def has_soil_evidence(crop, soil):
    return _SOIL_EVIDENCE_LOOKUP.get((crop, soil), False)


# =====================================================================
# PART 3: THE FOUR SCORES FOR ONE CROP
# =====================================================================
def rotation_fit(candidate, last_crop, prev_crop, soil, lang="en"):
    R = S["rotation_points"]
    if candidate == last_crop:
        if prev_crop == candidate:
            return R["repeat"], say(lang, "same_third"), "none"
        return R["repeat"], say(lang, "same_again"), "none"
    pair = rotations[(rotations["previous_crop"] == last_crop) &
                     (rotations["next_crop"] == candidate) &
                     (rotations["soil"] == soil)]
    if len(pair) > 0:
        row = pair.iloc[0]
        pts = R["sourced_confirmed"] if row["confidence"] == "confirmed" else R["sourced_not_sure"]
        evidence = row["evidence"]
        if lang == "kn":
            evidence = EVIDENCE_KN.get((last_crop, candidate), evidence)
        return pts, evidence + say(lang, "source_tag", src=row["source"]), row["confidence"]
    if last_crop in crop_info:
        if crop_info[last_crop]["legume"] != crop_info[candidate]["legume"]:
            return R["legume_cereal_change"], say(lang, "legume_cereal"), "general rule"
        return R["same_type_change"], say(lang, "same_type"), "general rule"
    return R["no_data"], say(lang, "no_rot_data"), "none"


def soil_fit(candidate, soil, lang="en"):
    sw = WORDS[lang]["soils"].get(soil, soil)
    if has_soil_evidence(candidate, soil):
        return S["soil_points"]["evidence"], say(lang, "soil_yes", soil=sw)
    return S["soil_points"]["no_evidence"], say(lang, "soil_no", soil=sw)


def climate_fit(candidate, zone, season, irrigation, lang="en", water_overrides=None):
    z, lv = S["zones"][zone], S["level"]
    W_ = WORDS[lang]
    zw = W_["zones"][zone]
    demand = lv[_level(candidate, water_overrides=water_overrides)]
    if season == "kharif":
        stress = max(lv[z["dry_spell_risk"]], 2 - lv[z["rain_supply"]])
        stress_note = say(lang, "stress_kharif", zone=zw, dry=W_["levels"][z["dry_spell_risk"]],
                          supply=W_["levels"][z["rain_supply"]])
    else:
        stress = 2 - lv[z["rabi_stored_moisture"]]
        stress_note = say(lang, "stress_rabi", zone=zw, moist=W_["levels"][z["rabi_stored_moisture"]])
    penalty = min(demand, stress)
    notes = [stress_note]
    if irrigation and penalty > 0:
        penalty = max(0, penalty - S["irrigation_reduces_stress_penalty_by"])
        notes.append(say(lang, "irrigation"))
    wl = 0
    if (season == "kharif" and z["waterlogging_risk"] == "high"
            and candidate in S["waterlogging_sensitive"]):
        wl = S["waterlogging_penalty"]
        notes.append(say(lang, "waterlog"))
    points = max(0, S["climate_start"] - penalty - wl)
    return points, "; ".join(notes)


def water_use(candidate, lang="en", water_overrides=None):
    level = _level(candidate, water_overrides=water_overrides)
    return S["water_use_points"][level], say(lang, "water_use", level=WORDS[lang]["levels"][level])


# =====================================================================
# PART 4: THE MAIN FUNCTION (Sakshi calls this)
# =====================================================================
def recommend(zone, soil, season, last_crop, prev_crop=None,
              irrigation=False, priority="balanced", top_n=3, lang="en",
              water_overrides=None):
    if lang not in WORDS:
        raise ValueError(f"lang must be one of {list(WORDS)}")
    if zone not in S["zones"]:
        raise ValueError(f"zone must be one of {list(S['zones'])}")
    if season not in ("kharif", "rabi"):
        raise ValueError("season must be kharif or rabi")
    if priority not in S["priority_weights"]:
        raise ValueError(f"priority must be one of {list(S['priority_weights'])}")
    if last_crop not in crop_info and last_crop not in other_info:
        raise ValueError("last_crop is not in our crop lists")

    W = S["priority_weights"][priority]
    warnings = []
    n_with_evidence = sum(has_soil_evidence(c, soil) for c in crop_info)
    if n_with_evidence < len(crop_info) / 2:
        warnings.append(say(lang, "warn_soil", soil=WORDS[lang]["soils"].get(soil, soil)))
    if last_crop in other_info:
        warnings.append(say(lang, "warn_other", crop=crop_word(lang, last_crop)))

    ranked = []
    for cand, info in crop_info.items():
        if info["season"] != season:
            continue
        r_pts, r_why, r_conf = rotation_fit(cand, last_crop, prev_crop, soil, lang)
        s_pts, s_why = soil_fit(cand, soil, lang)
        c_pts, c_why = climate_fit(cand, zone, season, irrigation, lang, water_overrides=water_overrides)
        w_pts, w_why = water_use(cand, lang, water_overrides=water_overrides)
        total = (r_pts * W["rotation"] + s_pts * W["soil"] +
                 c_pts * W["climate"] + w_pts * W["water_use"])
        max_total = (MAX_PART_POINTS["rotation"] * W["rotation"] +
                     MAX_PART_POINTS["soil"] * W["soil"] +
                     MAX_PART_POINTS["climate"] * W["climate"] +
                     MAX_PART_POINTS["water_use"] * W["water_use"])
        ranked.append({
            "crop": cand, "name_kn": info["name_kn"], "total": total, "max_total": max_total,
            "parts": {
                "rotation": RotationScore(r_pts, r_why, r_conf),
                "soil": PartScore(s_pts, s_why),
                "climate": PartScore(c_pts, c_why),
                "water_use": PartScore(w_pts, w_why),
            },
            "water_confidence": info["water_confidence"],
        })
    ranked.sort(key=lambda x: -x["total"])
    if top_n is not None:
        if top_n <= 0:
            ranked = []
        elif len(ranked) > top_n:
            cutoff = ranked[top_n - 1]["total"]
            ranked = [x for x in ranked if x["total"] >= cutoff]
    for x in ranked:
        if x["water_confidence"] == "not_sure":
            warnings.append(say(lang, "warn_water", crop=crop_word(lang, x["crop"])))
    return {"inputs": dict(zone=zone, soil=soil, season=season, last_crop=last_crop,
                           prev_crop=prev_crop, irrigation=irrigation, priority=priority, lang=lang),
            "warnings": warnings, "ranked": ranked}


def show(result):
    print("INPUTS:", result["inputs"])
    for w in result["warnings"]:
        print("  WARNING:", w)
    for i, r in enumerate(result["ranked"], 1):
        print(f"{i}. {r['crop']} ({r['name_kn']})  score {r['total']} / {r['max_total']}")
        p = r["parts"]
        print(f"     rotation  {p['rotation'].points}: {p['rotation'].why}")
        print(f"     soil      {p['soil'].points}: {p['soil'].why}")
        print(f"     climate   {p['climate'].points}: {p['climate'].why}")
        print(f"     water use {p['water_use'].points}: {p['water_use'].why}")
    print()


def recommend_with_ties(**kw):
    r = recommend(**kw)
    ranked = r["ranked"]
    place = 0
    prev_total = None
    for i, x in enumerate(ranked):
        if x["total"] != prev_total:
            place = i + 1
            prev_total = x["total"]
        x["place"] = place
        x["tied"] = sum(1 for y in ranked if y["total"] == x["total"]) > 1
    return r


def compare_strategies(usual_crop=None, **kw):
    """3 strategies: the farmer's usual crop + the 2 best others. Changes no score."""
    kw.pop("top_n", None)
    lang = kw.get("lang", "en")
    r = recommend(top_n=10, **kw)
    ranked = r["ranked"]
    by = {x["crop"]: x for x in ranked}
    if usual_crop is not None and usual_crop in by:
        others = [x for x in ranked if x["crop"] != usual_crop][:2]
        picks = [("usual", "Your usual choice", by[usual_crop]),
                 ("alt_1", "Alternative 1", others[0]),
                 ("alt_2", "Alternative 2", others[1])]
    else:
        picks = [("alt_1", "Alternative 1", ranked[0]),
                 ("alt_2", "Alternative 2", ranked[1]),
                 ("alt_3", "Alternative 3", ranked[2])]
    label_texts = {"Your usual choice": say(lang, "strat_usual"),
                   "Alternative 1": say(lang, "strat_alt", n=1),
                   "Alternative 2": say(lang, "strat_alt", n=2),
                   "Alternative 3": say(lang, "strat_alt", n=3)}
    strength_keys = {"confirmed": "str_confirmed", "not_sure": "str_not_sure",
                     "general rule": "str_general", "none": "str_none"}
    totals = [x["total"] for _, _, x in picks]
    strategies = []
    for key, label, x in picks:
        crop, info, p = x["crop"], crop_info[x["crop"]], x["parts"]
        rot = p["rotation"]
        soil = p["soil"]
        clim = p["climate"]
        wat = p["water_use"]
        rot_pts, rot_why, rot_conf = rot.points, rot.why, rot.confidence
        benefits = [wat.why]
        if info["legume"] == "yes":
            benefits.append(say(lang, "legume_crop"))
        if str(info["root_depth_m"]) != "not_found":
            benefits.append(say(lang, "root_depth", depth=info["root_depth_m"]))
        gaps = [say(lang, "gap_no_data")]
        if info["water_confidence"] == "not_sure":
            gaps.append(say(lang, "gap_water"))
        if rot_conf in ("none", "general rule"):
            gaps.append(say(lang, "gap_rot"))
        if soil.points < S["soil_points"]["evidence"]:
            gaps.append(say(lang, "gap_soil"))
        risks = [clim.why]
        if rot_pts == S["rotation_points"]["repeat"]:
            risks.append(rot_why)
        risks.append(say(lang, "risk_review"))
        strategies.append({
            "key": key, "label": label, "label_text": label_texts[label], "crop": crop, "name_kn": x["name_kn"], "total": x["total"],
            "max_total": x["max_total"], "tied_with_another": totals.count(x["total"]) > 1,
            "why": [rot_why, soil.why, clim.why, wat.why],
            "evidence": rot_why if rot_conf in ("confirmed", "not_sure") else say(lang, "ev_none"),
            "evidence_strength": say(lang, strength_keys[rot_conf]),
            "benefits": benefits, "gaps": gaps, "risks": risks})
    return {"inputs": r["inputs"], "warnings": r["warnings"], "strategies": strategies}


def assumption_check(water_overrides=None, **kw):
    """Does the best choice stay the same if the unconfirmed water needs are wrong?
    Tries 'low' and 'high' for every crop marked not_sure, then restores. Changes no saved setting."""
    kw.pop("top_n", None)

    def best(overrides=None):
        ranked = recommend(top_n=10, water_overrides=overrides, **kw)["ranked"]
        top = ranked[0]["total"]
        return sorted(x["crop"] for x in ranked if x["total"] == top), top

    unsure = [c for c, i in crop_info.items() if i["water_confidence"] == "not_sure"]
    base, base_total = best(water_overrides)
    outcomes = {}
    for level in ("low", "high"):
        overrides = dict(water_overrides or {})
        overrides.update({c: level for c in unsure})
        outcomes[level] = best(overrides)[0]
    stable = base == outcomes["low"] == outcomes["high"]
    msg = ("The best choice stays the same even if the unconfirmed water needs are lower or higher than we assumed."
           if stable else
           "The best choice depends on a water need that no expert has confirmed. Please ask a local expert.")
    return {"status": "stable" if stable else "changes", "best_now": base,
            "best_if_low": outcomes["low"], "best_if_high": outcomes["high"], "message": msg}
