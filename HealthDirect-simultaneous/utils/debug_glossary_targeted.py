import json
import os

# Paths are relative to the project workspace root
json_path = "glossary/glossary.json"

def debug_glossary(target_language: str, direction: str = "p_to_n") -> str:
    target_json = json_path
    if not os.path.exists(target_json) and os.path.exists("../" + json_path):
        target_json = "../" + json_path

    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found. Please run this script from the project root.")
        exit(1)

    with open(target_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        entries = data.get("glossary", [])

    formatted_lines = []
    target_lang_lower = target_language.lower()
    
    # First gather all raw candidate rules
    rules = []
    for entry in entries:
        english = entry.get("english", "")
        translations = entry.get("translations", {})
        description = entry.get("description", "")

        matched_lang_key = None
        for lang_key in translations.keys():
            if lang_key.lower() == target_lang_lower:
                matched_lang_key = lang_key
                break

        if matched_lang_key:
            translation = translations[matched_lang_key]
            if isinstance(translation, dict):
                formal_lang = translation.get("formal")
                informal_lang_list = []
                informal_raw = translation.get("informal")
                if informal_raw:
                    if isinstance(informal_raw, list):
                        informal_lang_list.extend(informal_raw)
                    elif isinstance(informal_raw, str):
                        informal_lang_list.append(informal_raw)

                formal_eng = english
                informal_eng_list = entry.get("informal_english", [])

                if direction == "p_to_n":
                    if formal_lang:
                        rules.append((formal_lang, formal_eng, description))
                    if informal_lang_list:
                        target_informal_eng = informal_eng_list[0] if (informal_eng_list and len(informal_eng_list) > 0) else formal_eng
                        for inf_lang in informal_lang_list:
                            rules.append((inf_lang, target_informal_eng, description))
                else:
                    if formal_lang:
                        rules.append((formal_eng, formal_lang, description))
                    if informal_eng_list and informal_lang_list:
                        for inf_eng in informal_eng_list:
                            rules.append((inf_eng, ", ".join(informal_lang_list), description))
                    elif informal_lang_list:
                        rules.append((formal_eng, ", ".join(informal_lang_list), description))
            else:
                translation_str = str(translation)
                if direction == "p_to_n":
                    rules.append((translation_str, english, description))
                else:
                    rules.append((english, translation_str, description))

    # Now deduplicate rules with priority logic
    unique_rules = {}
    for from_term, to_term, desc in rules:
        from_term_clean = from_term.strip().lower()
        if from_term_clean in unique_rules:
            existing_to = unique_rules[from_term_clean][1]
            
            # 1. 'extreme fire flame' always wins (demo override)
            if to_term.strip().lower() == "extreme fire flame":
                unique_rules[from_term_clean] = (from_term, to_term, desc)
            elif existing_to.strip().lower() == "extreme fire flame":
                pass
            # 2. 'headache' (singular) overrides 'headaches' (plural) for natural clinical conversation
            elif to_term.strip().lower() == "headache":
                unique_rules[from_term_clean] = (from_term, to_term, desc)
            elif existing_to.strip().lower() == "headache":
                pass
            else:
                unique_rules[from_term_clean] = (from_term, to_term, desc)
        else:
            unique_rules[from_term_clean] = (from_term, to_term, desc)

    # Format the deduplicated rules
    for from_term, to_term, desc in unique_rules.values():
        term_rule = f"{from_term} -> {to_term}"
        formatted_lines.append(f"- {term_rule}")

    return "\n".join(formatted_lines)

if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "German"
    dir_val = sys.argv[2] if len(sys.argv) > 2 else "p_to_n"
    
    print(f"=== {lang.upper()} {dir_val.upper()} GLOSSARY ===")
    print(debug_glossary(lang, direction=dir_val))
