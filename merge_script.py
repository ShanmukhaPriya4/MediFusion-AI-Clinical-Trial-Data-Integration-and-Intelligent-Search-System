import os
import json
import pandas as pd
from thefuzz import fuzz, process

# ---------- CONFIG ----------
CSV_FILE = "data.csv"
JSON_FOLDER = "json_files"
OUTPUT_FILE = "merged_output.json"

DOCTOR_FIELD = "Principal Investigator"
HOSPITAL_FIELD = "Name of Site"
# ----------------------------


def clean_name(name):
    """Normalize doctor/hospital names for matching."""
    if not isinstance(name, str):
        return ""
    return name.replace("Dr.", "").replace("Dr ", "").strip().lower()


def format_doctor_name(name):
    """Add 'Dr.' back with proper capitalization."""
    if not name:
        return name
    name = name.strip()
    if name.lower().startswith("dr"):
        return name  # Already formatted
    return "Dr. " + name.title()  # Ensure nice formatting
    


# Load CSV data
df_csv = pd.read_csv(CSV_FILE)
df_csv["clean_doc"] = df_csv[DOCTOR_FIELD].apply(clean_name)
df_csv["clean_hosp"] = df_csv[HOSPITAL_FIELD].apply(clean_name)

# Load JSON data
json_data = []
for file in os.listdir(JSON_FOLDER):
    if file.endswith(".json"):
        with open(os.path.join(JSON_FOLDER, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                json_data.extend(data)
            else:
                json_data.append(data)

# Match and merge
for record in json_data:

    doc_clean = clean_name(record.get(DOCTOR_FIELD, ""))
    hosp_clean = clean_name(record.get(HOSPITAL_FIELD, ""))

    # Try exact match
    matches = df_csv[
        (df_csv["clean_doc"] == doc_clean) & (df_csv["clean_hosp"] == hosp_clean)
    ]

    if not matches.empty:
        record.update(matches.iloc[0].to_dict())
    else:
        # Fuzzy match fallback
        best_doc = process.extractOne(doc_clean, df_csv["clean_doc"].tolist(), scorer=fuzz.ratio)
        best_hosp = process.extractOne(hosp_clean, df_csv["clean_hosp"].tolist(), scorer=fuzz.ratio)

        if best_doc and best_doc[1] > 85:
            matched_row = df_csv[df_csv["clean_doc"] == best_doc[0]]
            record.update(matched_row.iloc[0].to_dict())

    # Restore Dr. before saving
    record[DOCTOR_FIELD] = format_doctor_name(doc_clean)


# Remove helper columns before saving output
for rec in json_data:
    rec.pop("clean_doc", None)
    rec.pop("clean_hosp", None)

# Save final JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=4)

print("\n✨ Done! Output created:", OUTPUT_FILE)
print("Doctor names now include 'Dr.'")
