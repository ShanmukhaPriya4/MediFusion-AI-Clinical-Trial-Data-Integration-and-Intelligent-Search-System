import os
import json
import re
import csv
from collections import OrderedDict

# =========================
# PATHS
# =========================
INPUT_FOLDERS = [
    r"H:\Priya\Amol Project\Json_files",
    r"H:\Priya\Amol Project\Json_url\JSON_url"
]

OUTPUT_BASE_DIR = r"H:\Priya\Amol Project\output"
JSON_OUT_DIR = os.path.join(OUTPUT_BASE_DIR, "json")
CSV_OUT_DIR = os.path.join(OUTPUT_BASE_DIR, "csv")

os.makedirs(JSON_OUT_DIR, exist_ok=True)
os.makedirs(CSV_OUT_DIR, exist_ok=True)

# =========================
# DISEASE KEYWORDS
# =========================
DISEASE_MAP = {
    "stroke": "Stroke",
    "psoriasis": "Psoriasis",
    "diabetes": "Diabetes Mellitus",
    "hypertension": "Hypertension",
    "breast cancer": "Breast Cancer",
    "ovarian cancer": "Ovarian Cancer",
    "renal cell carcinoma": "Renal Cancer",
    "lupus nephritis": "Lupus Nephritis",
    "tuberculosis": "Tuberculosis",
    "epilepsy": "Epilepsy",
    "schizophrenia": "Schizophrenia",
    "glaucoma": "Glaucoma",
    "autism": "Autism Spectrum Disorder",
    "pcos": "Polycystic Ovary Syndrome",
    "osteoporosis": "Osteoporosis",
    "anemia": "Anemia",
    "periodontitis": "Periodontitis",
    "gingivitis": "Gingivitis"
}

# =========================
# DOMAIN RULES
# =========================
DOMAIN_RULES = {
    "anesthesia": "Anesthesiology",
    "anaesthesia": "Anesthesiology",
    "laryngoscopy": "Anesthesiology",
    "epidural": "Anesthesiology",
    "nerve block": "Anesthesiology",

    "mri": "Radiology",
    "ultrasound": "Radiology",
    "doppler": "Radiology",

    "neonate": "Neonatology",
    "bilirubin": "Neonatology",

    "psychiatric": "Psychiatry",
    "stress": "Mental Health",
    "anxiety": "Mental Health",

    "dental": "Dentistry",
    "periodontal": "Dentistry",

    "fracture": "Orthopedics",
    "arthroplasty": "Orthopedics",

    "questionnaire": "Medical Education",
    "perception": "Medical Education"
}

# =========================
# PATTERNS
# =========================
PATTERNS = [
    r"patients with ([a-zA-Z ]+)",
    r"treatment of ([a-zA-Z ]+)",
    r"management of ([a-zA-Z ]+)",
    r"in ([a-zA-Z ]+)"
]

STOP_WORDS = {
    "study", "trial", "randomized", "controlled", "clinical",
    "evaluation", "effect", "efficacy", "safety",
    "patients", "subjects", "using"
}

# =========================
# EXTRACTION LOGIC
# =========================
def extract_therapeutic_area(title):
    if not title or not isinstance(title, str):
        return "Unknown"

    text = title.lower()

    for k, v in DISEASE_MAP.items():
        if k in text:
            return v

    for k, v in DOMAIN_RULES.items():
        if k in text:
            return v

    for pattern in PATTERNS:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            words = [w for w in candidate.split() if w not in STOP_WORDS]
            if words:
                return " ".join(words[:4]).title()

    return "Unknown"

# =========================
# FILE PROCESSING
# =========================
def process_file(input_path, json_out_path, csv_out_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    enriched = []
    csv_rows = []

    for record in data:
        title = record.get("Scientific Title of Study", "")
        therapeutic_area = extract_therapeutic_area(title)

        new_record = OrderedDict(record)
        new_record["therapeutic_area"] = therapeutic_area
        enriched.append(new_record)

        csv_rows.append({
            "Scientific Title of Study": title,
            "therapeutic_area": therapeutic_area
        })

    # Write JSON
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    # Write CSV
    with open(csv_out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Scientific Title of Study", "therapeutic_area"]
        )
        writer.writeheader()
        writer.writerows(csv_rows)

# =========================
# RUNNER
# =========================
def process_all():
    for folder in INPUT_FOLDERS:
        for file in os.listdir(folder):
            if file.endswith(".json"):
                base_name = os.path.splitext(file)[0]

                process_file(
                    os.path.join(folder, file),
                    os.path.join(JSON_OUT_DIR, base_name + "_enriched.json"),
                    os.path.join(CSV_OUT_DIR, base_name + "_therapeutic_area.csv")
                )

if __name__ == "__main__":
    process_all()
    print("Completed")
