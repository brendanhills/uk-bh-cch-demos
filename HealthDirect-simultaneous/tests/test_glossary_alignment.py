import os
import json
import csv
from import_glossary import load_glossary_json

def test_local_glossary_json_and_csv_alignment():
    """Verify that the local glossary.json and glossary.csv contain matching numbers of translated terms."""
    json_path = "glossary/glossary.json"
    csv_path = "glossary/glossary.csv"
    
    assert os.path.exists(json_path), f"Local {json_path} does not exist!"
    assert os.path.exists(csv_path), f"Local {csv_path} does not exist!"
    
    # 1. Load JSON database
    glossary = load_glossary_json(json_path)
    
    # 2. Parse CSV database
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    headers = reader[0]
    csv_rows = reader[1:]
    
    # Header should start with 'en'
    assert headers[0] == "en"
    csv_languages = headers[1:] # e.g., ['es', 'vi', 'ar', 'de', 'hi', 'ja']
    
    # Map from standard code to language name in JSON
    code_to_name_map = {
        "es": "Spanish",
        "vi": "Vietnamese",
        "ar": "Arabic",
        "de": "German",
        "hi": "Hindi",
        "ja": "Japanese",
    }
    
    # 3. Verify that the count of fully-translated entries in JSON matches the exact number of rows in the CSV.
    fully_translated_count_in_json = 0
    for term, data in glossary.items():
        translations = data.get("translations", {})
        is_fully_translated = True
        
        # Check if term has non-empty values for all active CSV languages
        for code in csv_languages:
            lang_name = code_to_name_map.get(code)
            if not lang_name:
                continue
            
            trans_val = translations.get(lang_name, "")
            if isinstance(trans_val, dict):
                is_populated = bool(trans_val.get("formal") or trans_val.get("informal"))
            else:
                is_populated = bool(str(trans_val).strip())
                
            if not is_populated:
                is_fully_translated = False
                break
                
        if is_fully_translated:
            fully_translated_count_in_json += 1
            
    assert len(csv_rows) == fully_translated_count_in_json, (
        f"Alignment mismatch: JSON has {fully_translated_count_in_json} fully translated terms "
        f"for {csv_languages}, but CSV has {len(csv_rows)} rows!"
    )
