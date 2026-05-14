import os
import json
import re
import csv

# =========================
# PATHS
# =========================
INPUT_FOLDERS = [
    r"H:\Priya\Amol Project\Json_files",
    r"H:\Priya\Amol Project\Json_url\JSON_url"
]

OUTPUT_FILE = r"H:\Priya\Amol Project\unknown_therapeutic_area.csv"

# =========================
# THERAPEUTIC AREA KEYWORDS
# (same logic as main script)
# =========================
THERAPEUTIC_MAP = {
    "Cardiology": [
        "heart", "cardiac", "hypertension", "myocardial", "atrial", "stroke"
    ],
    "Endocrinology": [
        "diabetes", "insulin", "glycemic", "prediabetes", "thyroid"
    ],
    "Oncology": [
        "cancer", "carcinoma", "tumor", "chemotherapy", "oncology", "neoplasm"
    ],
    "Pulmonology": [
        "asthma", "tuberculosis", "lung", "respiratory", "pulmonary"
    ],
    "Neurology": [
        "epilepsy", "stroke", "parkinson", "neuropathy", "cognitive"
    ],
    "Psychiatry": [
        "stress", "anxiety", "depression", "mental", "psychiatric"
    ],
    "Orthopedics": [
        "fracture", "arthritis", "osteoporosis", "knee", "hip"
    ],
    "Dermatology": [
        "psoriasis", "vitiligo", "acne", "skin", "dermatitis"
    ],
    "Gynecology": [
        "pregnancy", "gestational", "pcos", "menstruation", "uterine"
    ],
    "Pediatrics": [
        "children", "neonate", "infant", "pediatric"
    ],
    "Public Health": [
        "knowledge", "attitude", "practice", "prevalence", "awareness"
    ],
    "Nutrition": [
        "dietary", "nutrition", "malnutrition", "supplementation"
    ]
}

# =========================
# EXTRACTION FUNCTION
# =========================
def extract_therapeutic_area(title):
    if not title or not isinstance(title, str):
        return "Unknown"

    text = title.lower()

    for area, keywords in THERAPEUTIC_MAP.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                return area

    return "Unknown"

# =========================
# PROCESS FILES
# =========================
rows = []
total = 0

for folder in INPUT_FOLDERS:
    for file in os.listdir(folder):
        if not file.endswith(".json"):
            continue

        path = os.path.join(folder, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            data = [data]

        for record in data:
            title = record.get("Scientific Title of Study", "").strip()
            if not title:
                continue

            area = extract_therapeutic_area(title)

            if area == "Unknown":
                rows.append([title])
                total += 1

# =========================
# WRITE CSV
# =========================
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Scientific Title of Study"])
    writer.writerows(rows)

print("Completed")
print("Unknown records:", total)
print("Output file:", OUTPUT_FILE)
