import os
import json
import pandas as pd

# -------------------------
# Step 1: Combine all JSON files
# -------------------------
folder_path = r"H:\Priya\Amol Project"  # Update this path
all_data = []

for filename in os.listdir(folder_path):
    if filename.startswith("batch_") and filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        print(f"Processing {filename}")
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")

# Save combined JSON
output_file = os.path.join(folder_path, "combined_data.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4)
print(f"Combined {len(all_data)} records into {output_file}")

# -------------------------
# Step 2: Convert to DataFrame
# -------------------------
df = pd.DataFrame(all_data)

# -------------------------
# Step 3: Define helper functions
# -------------------------
def extract_investigators(x):
    investigators = []
    if isinstance(x, dict) and "Name of Principal Investigator" in x:
        investigators.append(x["Name of Principal Investigator"])
    elif isinstance(x, list):
        for d in x:
            if isinstance(d, dict) and "Name of Principal Investigator" in d:
                investigators.append(d["Name of Principal Investigator"])
    return investigators

def extract_sponsors(x):
    sponsors = []
    if isinstance(x, dict) and "Name" in x:
        sponsors.append(x["Name"])
    elif isinstance(x, list):
        for d in x:
            if isinstance(d, dict) and "Name" in d:
                sponsors.append(d["Name"])
    return sponsors

def extract_cros(x):
    cros = []
    if isinstance(x, dict) and "Name" in x:
        cros.append(x["Name"])
    elif isinstance(x, list):
        for d in x:
            if isinstance(d, dict) and "Name" in d:
                cros.append(d["Name"])
    return cros

def extract_sites(x):
    sites = []
    if isinstance(x, dict) and "Name of Site" in x:
        sites.append(x["Name of Site"])
    elif isinstance(x, list):
        for d in x:
            if isinstance(d, dict) and "Name of Site" in d:
                sites.append(d["Name of Site"])
    return sites

# -------------------------
# Step 4: Flatten fields
# -------------------------
df['Investigator_List'] = df['Principal Investigator'].apply(lambda x: extract_investigators(x))
df['Sponsor_List'] = df['Primary Sponsor'].apply(lambda x: extract_sponsors(x))
df['CRO_List'] = df['Details of Secondary Sponsor'].apply(lambda x: extract_cros(x))
df['Sites_List'] = df['Sites of Study'].apply(lambda x: extract_sites(x))

# -------------------------
# Step 5: Analytics
# -------------------------
total_sites = sum(df['Sites_List'].apply(len))
total_investigators = len(set(sum(df['Investigator_List'], [])))
total_sponsors = len(set(sum(df['Sponsor_List'], [])))
total_cros = len(set(sum(df['CRO_List'], [])))

print(f"Total Sites: {total_sites}")
print(f"Total Investigators: {total_investigators}")
print(f"Total Sponsors: {total_sponsors}")
print(f"Total CROs: {total_cros}")

# -------------------------
# Step 6: Trial details per year
# -------------------------
# Assuming 'CTRI Number' contains the year like 'CTRI/2024/...'
df['Year'] = df['CTRI Number'].str.extract(r'CTRI/(\d{4})/')
trials_per_year = df['Year'].value_counts().sort_index()
print("\nNumber of Trials per Year:")
print(trials_per_year)

# -------------------------
# Step 7: Sites per trial
# -------------------------
df_exploded = df.explode('Sites_List')
sites_per_trial = df_exploded.groupby('CTRI Number')['Sites_List'].nunique()
max_sites_per_year = df_exploded.groupby('Year')['Sites_List'].nunique()
print("\nMaximum number of sites per trial:")
print(sites_per_trial)
print("\nMaximum sites per year:")
print(max_sites_per_year)
