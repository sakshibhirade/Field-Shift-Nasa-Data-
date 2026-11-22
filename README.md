# Field Shift — a crop rotation helper for Belagavi district

**Team Galactic Geeks — NASA Space Apps Challenge 2026**  
**Challenge:** Field Shift: Adapting Farms with NASA Data

**Team Members:** Sifa Kotwal, Sakshi Bhirade, Amulya B.K., Bushra Soudagar, Asmiya Bepari  
**Institution:** KLE Society's College of Computer Applications, Belagavi

## What it is

A decision-support tool for farmers in Belagavi district. A farmer enters taluk, soil, season, last crop, irrigation, and what matters most (soil health, saving water, or a safe harvest). The tool scores each crop on four things — rotation, soil, climate, and water use — shows the best crops, compares three strategies (their usual crop and the two best others, each with why, evidence, benefits, information gaps, and risks), and tells the farmer if the best choice would change when an unconfirmed water need is lower or higher than assumed.

It supports the farmer and the local agriculture office. It does not replace them.

It works in Kannada and English. It is a clear point-scoring system, not machine learning. All weights and thresholds are kept in one settings block in `scoring.py`.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run the tests

```bash
python check_tests.py
```

Expected: **ALL PASS** — 5 fixed test cases, plus the assumption check for the first case: changes, now `[chickpea, rabi_jowar]`, low `[chickpea]`, high `[rabi_jowar]`.

## NASA data used

NASA POWER daily data, 1981–2025, at three points: Belagavi, Khanapur (west, wet), and Athani (east, dry). NASA POWER is a model estimate, so we use it only to compare zones and years, not to give exact rain.

What it shows, recalculated from the yearly files in `data/`:

- Dry spell of 7+ days in July–August: Athani 38 of 45 years, Belagavi 12 of 45, Khanapur 10 of 45.
- Low stored soil moisture on 1 October (root-zone wetness below 0.8, our own cut-off): Athani 38 of 45 years, Belagavi 9 of 45, Khanapur 9 of 45.
- Warming of about 0.11 to 0.13 °C per decade in all three zones.
- Monsoon rain is rising only in Khanapur, under two tests. Belagavi and Athani show no reliable rain trend.
- We do not quote absolute rainfall in mm: NASA POWER appears to overstate absolute rain compared with station records (unverified), so we use risky-year counts instead.
- The droughts of 2003 and 2015 and the floods of 2019 show up in this NASA POWER data as deficit/excess years in all three zones.

Chart: `evidence_simple.png` (45 squares per zone).

### Next step

Cross-check these zones with NASA SMAP soil moisture, GPM IMERG rainfall, and NDVI. Many other datasets on the challenge resource list (for example Web Soil Survey, SSURGO, and PRISM) cover only the United States, so for local soil and crop facts we used Indian sources: UAS Dharwad and ICAR documents, and one KVK expert.

## Local sources

- **Rotations:** UAS Dharwad district contingency plan and ICAR documents, for black soil. They list these pairs as common systems on black soil, not as advice written specifically for Belagavi.
- **Expert:** Dr. D. A. Mhetre, Senior Scientist and Head, ICAR-BIRDS KVK Tukkanatti, Belagavi.
- Contact was through WhatsApp with our teammate Amulya on 22 October and 31 October 2026, with a follow-up reply on 2 November 2026.
- He allowed us to use his name and suggested corrections, including sugarcane-based cropping, intercropping with pulses and oilseeds, and rotation after sugarcane. He said soybean residue leaves nitrogen in the soil, and for Athani advised soybean with pigeon pea, and chickpea or rabi jowar in rabi if water is available.
- His two answers on water order were not fully consistent, and he did not answer our follow-up on whether the order changes by zone, so we did not use his water order for the scores.
- **Taluk-to-zone map:** from a 2011 CRIDA plan, not yet opened by the team. It lists 10 taluks; the district may have 15. If a taluk is not listed, choose the nearest one — results are approximate.

## Honest limits

- The water need of chickpea, green gram, and black gram is not confirmed by an expert, so the tool treats it as medium and warns about it. That is why several choices come out equal.
- Pigeon pea and mixed cropping are not in the tool yet, and neither is sugarcane. The KVK expert advised all three.
- No sourced rotations for red soil, or for rabi followed by kharif.
- No yield, price, or profit numbers — we have none.
- The Kannada text was checked by a Kannada-speaking team member, not an independent reviewer.
- No verified Belagavi farmer interviews yet. Our interview questions are ready; testing with Belagavi farmers is a next step. Do not treat sample answers in our interview draft as real farmer quotes.

## AI use

AI tools helped with code, Kannada drafts, research summaries, and report and slide drafts. All numbers, scores, and claims in this repository were checked by the team against the files in `data/` and the sources above. No AI-generated images are used in the project.


