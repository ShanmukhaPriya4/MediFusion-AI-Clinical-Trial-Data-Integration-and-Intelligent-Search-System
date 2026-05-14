import spacy
import json
import csv
import os
import glob
import re
import warnings

warnings.filterwarnings("ignore")

# -------------------------------
# Load Models
# -------------------------------
print("Loading models...")
nlp_bc5 = spacy.load("en_ner_bc5cdr_md")
nlp_jnlpba = spacy.load("en_ner_jnlpba_md")
print("Models loaded successfully.\n")

# -------------------------------
# Input & Output Paths
# -------------------------------
input_folder = r"D:\Priya\Amol Project\Json_url\JSON_url"
output_folder = r"D:\Priya\Amol Project\output12"
os.makedirs(output_folder, exist_ok=True)

batch_files = glob.glob(os.path.join(input_folder, "batch_*_extracted.json"))

# Sort numerically (important fix)
batch_files = sorted(
    batch_files,
    key=lambda x: int(re.search(r"batch_(\d+)_", x).group(1))
)

print(f"Found {len(batch_files)} batch files.\n")

processed_batches = []

# -------------------------------
# Helper Functions
# -------------------------------
def clean_entity(text):
    return text.strip().replace("\n", " ")

def is_valid_drug(text):
    drug_suffixes = (
        "mab", "nib", "vir", "olol", "pril",
        "sartan", "cillin", "oxetine", "azole",
        "statin", "mycin", "prostol"
    )

    text = text.strip()

    if text.lower().endswith(drug_suffixes):
        return True

    if text.isupper() and len(text) > 4:
        return True

    return False

def is_valid_disease(text):
    text = text.strip()

    if len(text) < 4:
        return False

    if text.isupper() and len(text) <= 4:
        return False

    return True

# -------------------------------
# Process Each Batch
# -------------------------------
for input_file in batch_files:

    match = re.search(r"batch_(\d+)_extracted\.json", input_file)
    if not match:
        print(f"Skipping (pattern mismatch): {input_file}")
        continue

    batch_number = match.group(1)
    processed_batches.append(int(batch_number))

    print(f"\nProcessing Batch {batch_number}")

    json_output = os.path.join(
        output_folder, f"drug_therapeutic_area_{batch_number}.json"
    )
    csv_output = os.path.join(
        output_folder, f"drug_therapeutic_area_{batch_number}.csv"
    )

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        continue

    results = []
    total_records = len(data)
    print(f"Total records: {total_records}")

    for index, entry in enumerate(data, start=1):

        title = entry.get("Scientific Title of Study", "").strip()
        if not title:
            continue

        drugs = set()
        diseases = set()

        # BC5CDR Model
        doc1 = nlp_bc5(title)
        for ent in doc1.ents:
            if ent.label_ == "CHEMICAL":
                drugs.add(clean_entity(ent.text))
            elif ent.label_ == "DISEASE":
                if is_valid_disease(ent.text):
                    diseases.add(clean_entity(ent.text))

        # JNLPBA Model
        doc2 = nlp_jnlpba(title)
        for ent in doc2.ents:
            if ent.label_ == "PROTEIN":
                if is_valid_drug(ent.text):
                    drugs.add(clean_entity(ent.text))

        results.append({
            "title": title,
            "drug_used": sorted(drugs),
            "therapeutic_area": sorted(diseases)
        })

        if index % 200 == 0:
            print(f"  Processed {index}/{total_records}")

    # Save JSON
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    # Save CSV
    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Drug Used", "Therapeutic Area"])

        for row in results:
            writer.writerow([
                row["title"],
                ", ".join(row["drug_used"]),
                ", ".join(row["therapeutic_area"])
            ])

    print(f"Batch {batch_number} completed.")

# -------------------------------
# Final Summary
# -------------------------------
print("\nAll batches processed successfully.")

if processed_batches:
    print(f"Processed batch numbers: {sorted(processed_batches)}")
    print(f"Total processed batches: {len(processed_batches)}")