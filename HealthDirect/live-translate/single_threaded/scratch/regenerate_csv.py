import json
import csv
import os

json_path = "glossary/glossary.json"
csv_path = "glossary/glossary.csv"

if not os.path.exists(json_path):
    print(f"Error: {json_path} not found.")
    exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    entries = data.get("glossary", [])

# Collect all available languages in translations
languages = set()
for entry in entries:
    for lang in entry.get("translations", {}).keys():
        languages.add(lang)

# We want a standard column structure: English, followed by other languages in alphabetical order
sorted_langs = sorted(list(languages))
headers = ["english"] + sorted_langs

# Write to CSV
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    
    for entry in entries:
        english = entry.get("english", "")
        row = [english]
        translations = entry.get("translations", {})
        
        for lang in sorted_langs:
            val = translations.get(lang, "")
            if isinstance(val, dict):
                # Format formal/informal dictionaries nicely as text, e.g. "Formal: Pyrexie | Informal: Fieber"
                formal = val.get("formal", "")
                informal_list = val.get("informal", [])
                if isinstance(informal_list, str):
                    informal_list = [informal_list]
                
                parts = []
                if formal:
                    parts.append(f"formal: {formal}")
                if informal_list:
                    parts.append(f"informal: {', '.join(informal_list)}")
                row.append(" | ".join(parts))
            else:
                row.append(str(val))
        
        writer.writerow(row)

print(f"Successfully exported {len(entries)} glossary entries to {csv_path}!")
