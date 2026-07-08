import json
import os
import sys

# Add the scratch directory to sys.path to allow importing add_colloquial_terms
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import COLLOQUIAL_DATA from add_colloquial_terms
from add_colloquial_terms import COLLOQUIAL_DATA

def main():
    json_path = "dictionary/glossary.json"
    csv_path = "dictionary/glossary.csv"
    
    if not os.path.exists(json_path):
        print(f"[ERROR] glossary.json not found at {json_path}")
        sys.exit(1)
        
    print(f"Loading glossary database from '{json_path}'...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    glossary_list = data.get("glossary", [])
    print(f"  Loaded {len(glossary_list)} existing terminology entries.")
    
    # Create a case-insensitive lookup of existing terms
    # Maps lowercase term name to its entry dict
    lookup = {entry["english"].lower().strip(): entry for entry in glossary_list}
    
    added_count = 0
    skipped_count = 0
    
    for item in COLLOQUIAL_DATA:
        formal_eng = item["english"]
        formal_key = formal_eng.lower().strip()
        
        # Get the formal entry if it exists in the database
        formal_entry = lookup.get(formal_key)
        if not formal_entry:
            print(f"  [INFO] Formal term '{formal_eng}' not found in database. Creating it.")
            # Create a formal entry first
            formal_translations = {}
            for lang, val in item["translations"].items():
                formal_translations[lang] = val["formal"]
            formal_entry = {
                "english": formal_eng,
                "translations": formal_translations,
                "description": item["description"]
            }
            glossary_list.append(formal_entry)
            lookup[formal_key] = formal_entry
            added_count += 1
            
        # Create duplicate entries for each informal synonym
        for i, informal_eng in enumerate(item["informal_english"]):
            informal_key = informal_eng.lower().strip()
            
            if informal_key in lookup:
                # Already exists, skip
                skipped_count += 1
                continue
                
            # Construct the translations dictionary for this informal term
            informal_translations = {}
            
            # Map translations
            for lang, val in item["translations"].items():
                if "informal" in val and len(val["informal"]) > i:
                    informal_translations[lang] = val["informal"][i]
                else:
                    informal_translations[lang] = val["formal"]
                    
            # Fallback for other languages already present in formal_entry's translations
            for lang, trans_val in formal_entry.get("translations", {}).items():
                if lang not in informal_translations:
                    informal_translations[lang] = trans_val
                    
            # Construct description referencing the formal term
            desc = f"Colloquial/informal term for {formal_eng}."
            if item.get("description"):
                desc += f" {item['description']}"
                
            new_entry = {
                "english": informal_eng,
                "translations": informal_translations,
                "description": desc
            }
            
            # Also inherit any grounding fields or other fields if present in formal_entry
            for field in [
                "url", "Spanish_grounding_url", "Spanish_grounding_snippet",
                "Vietnamese_grounding_url", "Vietnamese_grounding_snippet"
            ]:
                if formal_entry.get(field):
                    new_entry[field] = formal_entry[field]
                    
            glossary_list.append(new_entry)
            lookup[informal_key] = new_entry
            added_count += 1
            
    print(f"Duplication Summary:")
    print(f"  - Brand-new entries created (formal or informal): {added_count}")
    print(f"  - Skipped (already existed): {skipped_count}")
    print(f"  - Total glossary entries: {len(glossary_list)}")
    
    # Save the updated glossary.json (preserving existing casing and ordering)
    print(f"Saving updated glossary database to '{json_path}'...")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"glossary": glossary_list}, f, indent=2, ensure_ascii=False)
    print("  Save complete.")
    
    # Compile and save the 3-column CSV (English, Spanish, Vietnamese)
    # Using exact logic of import_glossary's export_to_csv, but loading directly
    print(f"Compiling and writing multi-lingual CSV to '{csv_path}'...")
    import csv
    export_count = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["en", "es", "vi"])
        for entry in glossary_list:
            term = entry.get("english", "").strip()
            translations = entry.get("translations", {})
            es_trans = translations.get("Spanish", "").strip()
            vi_trans = translations.get("Vietnamese", "").strip()
            if term and es_trans and vi_trans:
                writer.writerow([term, es_trans, vi_trans])
                export_count += 1
                
    print(f"  Successfully compiled and wrote {export_count} rows to CSV.")

if __name__ == "__main__":
    main()
