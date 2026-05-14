import pandas as pd
import re

df = pd.read_csv("Sites_cleaned_final678.csv")

def format_name(name):
    name = str(name).strip()
    if not re.match(r'(?i)^dr[\.\s]', name):
        name = 'Dr ' + name
    name = re.sub(r'(?i)^dr[\.\s]*', 'Dr ', name)
    return name.strip()

df['Name of Principal Investigator'] = df['Name of Principal Investigator'].apply(format_name)

df.to_csv("Sites_final_with_dr678.csv", index=False)

print("✅ Names updated and saved in 'Sites_final_with_dr.csv'")





