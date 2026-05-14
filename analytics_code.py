import os
import json
import pandas as pd

# ------------------ Step 1: Load all JSON batch files ------------------

folder_paths = [
    r"H:\Priya\Amol Project\Json_files",
    r"H:\Priya\Amol Project\Json_url\JSON_url"
]

all_data = []

for folder_path in folder_paths:
    if not os.path.exists(folder_path):
        continue

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.startswith("batch_") and filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_data.extend(data)
                        else:
                            all_data.append(data)
                    except json.JSONDecodeError:
                        pass

print(f"Total records loaded: {len(all_data)}")

# ------------------ Step 2: Normalize JSON ------------------

df = pd.json_normalize(all_data)

# ------------------ Step 3: Exact column mapping ------------------

trial_id_col = 'CTRI Number'
date_col = 'Last Modified On'
sites_col = 'Sites of Study'
cro_col = 'Details of Ethics Committee'
investigator_col = 'Principal Investigator.Name'
sponsor_col = 'Primary Sponsor.Name'

# ------------------ Step 4: Create YEAR column ------------------

df['trial_year'] = pd.to_datetime(
    df[date_col],
    dayfirst=True,
    errors='coerce'
).dt.year

# ------------------ Step 5: Compute NUMBER OF SITES per trial ------------------

def count_sites(x):
    if isinstance(x, list):
        return len(x)
    elif isinstance(x, str):
        return len([s for s in x.split(',') if s.strip()])
    return 0

df['num_sites'] = df[sites_col].apply(count_sites)

# ------------------ Step 6: Flatten key columns ------------------

df['site_flat'] = df[sites_col].astype(str)
df['investigator_flat'] = df[investigator_col].astype(str)
df['cro_flat'] = df[cro_col].astype(str)
df['sponsor_flat'] = df[sponsor_col].astype(str)

# ------------------ TABLE 1: SUMMARY TABLE ------------------

summary_table = pd.DataFrame({
    "Metric": [
        "Total Sites",
        "Total Investigators",
        "Total CROs (Ethics Committees)",
        "Total Sponsors"
    ],
    "Value": [
        df['site_flat'].nunique(),
        df['investigator_flat'].nunique(),
        df['cro_flat'].nunique(),
        df['sponsor_flat'].nunique()
    ]
})

print("\n===== SUMMARY TABLE =====")
print(summary_table)

summary_table.to_csv("summary_table.csv", index=False)

# ------------------ TABLE 2: NUMBER OF TRIALS PER YEAR ------------------

trials_per_year = (
    df[df['trial_year'] >= 2007]
    .groupby('trial_year')[trial_id_col]
    .nunique()
    .reset_index(name="Number of Trials")
    .sort_values('trial_year')
)

print("\n===== NUMBER OF TRIALS PER YEAR (2007 TO DATE) =====")
print(trials_per_year)

trials_per_year.to_csv("trials_per_year.csv", index=False)

# ------------------ TABLE 3A: SITE DISTRIBUTION PER YEAR ------------------

site_distribution = (
    df[df['trial_year'] >= 2007]
    .groupby(['trial_year', 'num_sites'])
    .size()
    .reset_index(name="Number of Trials")
    .sort_values(['trial_year', 'num_sites'])
)

print("\n===== NUMBER OF TRIALS BY SITE COUNT PER YEAR =====")
print(site_distribution)

site_distribution.to_csv("site_distribution_per_year.csv", index=False)

# ------------------ TABLE 3B: MAX SITES PER YEAR ------------------

max_sites_per_year = (
    df[df['trial_year'] >= 2007]
    .groupby('trial_year')['num_sites']
    .max()
    .reset_index(name="Maximum Sites in a Trial")
    .sort_values('trial_year')
)

print("\n===== MAXIMUM NUMBER OF SITES IN A SINGLE TRIAL PER YEAR =====")
print(max_sites_per_year)

max_sites_per_year.to_csv("max_sites_per_year.csv", index=False)

print("\n All output tables exported as CSV files successfully.")
