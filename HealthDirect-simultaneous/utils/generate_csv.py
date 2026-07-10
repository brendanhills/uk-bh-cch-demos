import json
import csv
import os

# Paths are relative to the project workspace root
json_path = "glossary/glossary.json"
csv_path = "glossary/glossary.csv"

def regenerate_csv():
    # If run from inside the utils directory, adjust paths to project root
    target_json = json_path
    target_csv = csv_path
    if not os.path.exists(target_json) and os.path.exists("../" + json_path):
        target_json = "../" + json_path
        target_csv = "../" + csv_path

    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found. Please run this script from the project root.")
        exit(1)

    print(f"Loading clinical glossary from: {target_json}")
    with open(target_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        entries = data.get("glossary", [])

    # Collect all available languages in translations
    languages = set()
    for entry in entries:
        for lang in entry.get("translations", {}).keys():
            languages.add(lang)

    # Standard column structure: English, followed by other languages alphabetically
    sorted_langs = sorted(list(languages))
    headers = ["english"] + sorted_langs

    # Write to CSV
    print(f"Writing fully populated CSV to: {target_csv}")
    with open(target_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for entry in entries:
            english = entry.get("english", "")
            row = [english]
            translations = entry.get("translations", {})
            
            for lang in sorted_langs:
                val = translations.get(lang, "")
                if isinstance(val, dict):
                    # Format formal/informal dictionaries nicely as text
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

    print(f"Success! Exported {len(entries)} glossary entries to {target_csv}!")

if __name__ == "__main__":
    regenerate_csv()
