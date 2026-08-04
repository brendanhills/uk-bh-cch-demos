import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from demo.web_server import GLOSSARY_PATH
import json

def debug_load_and_format_glossary(target_language: str, direction: str = "n_to_p") -> str:
    with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
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

p_to_n = debug_load_and_format_glossary("German", direction="p_to_n")
n_to_p = debug_load_and_format_glossary("German", direction="n_to_p")

print("=== DEDUPLICATED PATIENT TO NURSE RULES ===")
for line in p_to_n.split("\n"):
    if any(word in line.lower() for word in ["headache", "cephalalgia", "fever", "fire", "flame", "fieber", "kopfschmerzen"]):
        print(line)

print("\n=== DEDUPLICATED NURSE TO PATIENT RULES ===")
for line in n_to_p.split("\n"):
    if any(word in line.lower() for word in ["headache", "cephalalgia", "fever", "fire", "flame", "fieber", "kopfschmerzen"]):
        print(line)
