import os
import json
import csv

# -------------------------
# INPUT: OUTPUT FOLDER
# -------------------------
OUTPUT_BASE_DIR = r"H:\Priya\Amol Project\output"

# -------------------------
# OUTPUT CSV
# -------------------------
OUTPUT_CSV = r"H:\Priya\Amol Project\scientific_title_therapeutic_area_index.csv"

rows = []

# -------------------------
# WALK THROUGH Json_files & JSON_url
# -------------------------
for root, _, files in os.walk(OUTPUT_BASE_DIR):
    source_folder = os.path.basename(root)

    for file_name in files:
        if not file_name.lower().endswith(".json"):
            continue

        file_path = os.path.join(root, file_name)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                for record in data:
                    rows.append([
                        source_folder,
                        file_name,
                        record.get("Scientific Title of Study", "").strip(),
                        record.get("therapeutic_area", "").strip()
                    ])

            elif isinstance(data, dict):
                rows.append([
                    source_folder,
                    file_name,
                    data.get("Scientific Title of Study", "").strip(),
                    data.get("therapeutic_area", "").strip()
                ])

        except Exception as e:
            rows.append([
                source_folder,
                file_name,
                "ERROR",
                str(e)
            ])

# -------------------------
# WRITE CSV
# -------------------------
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Source Folder",
        "File Name",
        "Scientific Title of Study",
        "Therapeutic Area"
    ])
    writer.writerows(rows)

print(" Done!")
print(f" CSV created at:\n{OUTPUT_CSV}")

                   