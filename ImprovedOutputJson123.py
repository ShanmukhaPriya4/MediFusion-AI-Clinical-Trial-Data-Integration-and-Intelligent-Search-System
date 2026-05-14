import spacy
import json
import csv
import os
import glob
import re
import requests
import warnings
import time

warnings.filterwarnings("ignore")

# -------------------------------
# ADD YOUR MEDICAL DICTIONARY API KEY
# -------------------------------
API_KEY = "4453de00-688a-4039-ae79-8733b5666002"

# -------------------------------
# Load NLP Models
# -------------------------------
print("Loading models...")

nlp_bc5 = spacy.load("en_ner_bc5cdr_md")
nlp_jnlpba = spacy.load("en_ner_jnlpba_md")

print("Models loaded successfully.\n")

# -------------------------------
# Input and Output Paths
# -------------------------------
input_folder = r"D:\Priya\Amol Project\Json_files"
output_folder = r"D:\Priya\Amol Project\ImprovedOutputJSON123"

os.makedirs(output_folder, exist_ok=True)

batch_files = glob.glob(os.path.join(input_folder, "batch_*_extracted.json"))

# Sort batch files numerically
batch_files = sorted(
    batch_files,
    key=lambda x: int(re.search(r"batch_(\d+)_", x).group(1))
)

print(f"Found {len(batch_files)} batch files\n")

# -------------------------------
# Synonym Cache
# -------------------------------
synonym_cache = {}

# -------------------------------
# Helper Functions
# -------------------------------

def clean_entity(text):
    return text.strip().replace("\n", " ")

def is_valid_drug(text):

    drug_suffixes = (
        "mab","nib","vir","olol","pril",
        "sartan","cillin","azole","statin","mycin"
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
# Get Medical Synonyms
# -------------------------------

def get_medical_synonyms(term):

    if term in synonym_cache:
        return synonym_cache[term]

    try:

        url = f"https://www.dictionaryapi.com/api/v3/references/medical/json/{term}?key={API_KEY}"

        response = requests.get(url)

        synonyms = set()

        if response.status_code == 200:

            data = response.json()

            for entry in data:

                if isinstance(entry, dict):

                    if "meta" in entry:

                        if "syns" in entry["meta"]:
                            for syn_list in entry["meta"]["syns"]:
                                for syn in syn_list:
                                    synonyms.add(syn.lower())

                        if "stems" in entry["meta"]:
                            for stem in entry["meta"]["stems"]:
                                synonyms.add(stem.lower())

        synonym_cache[term] = list(synonyms)

        time.sleep(0.1)

        return list(synonyms)

    except Exception as e:

        print(f"Error fetching synonyms for {term}: {e}")
        return []


# -------------------------------
# Process Each Batch
# -------------------------------

processed_batches = []

for input_file in batch_files:

    match = re.search(r"batch_(\d+)_extracted\.json", input_file)

    if not match:
        continue

    batch_number = match.group(1)

    print(f"\nProcessing Batch {batch_number}")

    json_output = os.path.join(
        output_folder,
        f"drug_therapeutic_area_{batch_number}.json"
    )

    csv_output = os.path.join(
        output_folder,
        f"drug_therapeutic_area_{batch_number}.csv"
    )

    with open(input_file,'r',encoding='utf-8') as f:
        data = json.load(f)

    results = []

    total_records = len(data)

    print(f"Total records: {total_records}")

    for index, entry in enumerate(data,start=1):

        title = entry.get("Scientific Title of Study","").strip()

        if not title:
            continue

        drugs = set()
        diseases = set()

        # -------------------------------
        # BC5CDR model extraction
        # -------------------------------

        doc1 = nlp_bc5(title)

        for ent in doc1.ents:

            if ent.label_ == "CHEMICAL":
                drugs.add(clean_entity(ent.text))

            elif ent.label_ == "DISEASE":
                if is_valid_disease(ent.text):
                    diseases.add(clean_entity(ent.text))


        # -------------------------------
        # JNLPBA model extraction
        # -------------------------------

        doc2 = nlp_jnlpba(title)

        for ent in doc2.ents:

            if ent.label_ == "PROTEIN":
                if is_valid_drug(ent.text):
                    drugs.add(clean_entity(ent.text))


        # -------------------------------
        # Synonym Expansion
        # -------------------------------

        disease_synonyms = {}

        for disease in diseases:

            synonyms = get_medical_synonyms(disease)

            disease_synonyms[disease] = synonyms


        results.append({

            "title": title,
            "drug_used": sorted(drugs),
            "therapeutic_area": sorted(diseases),
            "therapeutic_area_synonyms": disease_synonyms
        })


        if index % 200 == 0:
            print(f"Processed {index}/{total_records}")


    # -------------------------------
    # Save JSON
    # -------------------------------

    with open(json_output,'w',encoding='utf-8') as f:
        json.dump(results,f,indent=4)


    # -------------------------------
    # Save CSV
    # -------------------------------

    with open(csv_output,'w',newline='',encoding='utf-8') as f:

        writer = csv.writer(f)

        writer.writerow([
            "Title",
            "Drug Used",
            "Therapeutic Area",
            "Synonyms"
        ])

        for row in results:

            synonyms_flat = []

            for syn_list in row["therapeutic_area_synonyms"].values():
                synonyms_flat.extend(syn_list)

            writer.writerow([
                row["title"],
                ", ".join(row["drug_used"]),
                ", ".join(row["therapeutic_area"]),
                ", ".join(set(synonyms_flat))
            ])


    print(f"Batch {batch_number} completed")

print("\nAll batches processed successfully")