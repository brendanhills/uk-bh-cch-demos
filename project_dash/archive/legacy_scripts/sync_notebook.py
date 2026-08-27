#!/usr/bin/env python3
import json
import os
import sys
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NOTEBOOKS_DIR = os.path.join(DATA_DIR, "notebooks")
SHEETS_DIR = os.path.join(DATA_DIR, "sheets")
REGISTRY_PATH = os.path.join(NOTEBOOKS_DIR, "registry.json")

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def sync_notebook(notebook_id, title=None, slug=None, category=None, description=None):
    os.makedirs(NOTEBOOKS_DIR, exist_ok=True)
    registry = load_json(REGISTRY_PATH, {"activeNotebookId": notebook_id, "notebooks": []})
    
    # Locate or create notebook entry in registry
    nb_entry = next((nb for nb in registry.get("notebooks", []) if nb.get("id") == notebook_id or nb.get("slug") == slug), None)
    
    if not nb_entry:
        computed_slug = slug or f"notebook_{notebook_id[:8]}"
        computed_title = title or f"Gemini Notebook ({notebook_id[:8]})"
        nb_entry = {
            "id": notebook_id,
            "slug": computed_slug,
            "title": computed_title,
            "category": category or "General Knowledge",
            "description": description or f"Gemini Notebook knowledge base for {computed_title}",
            "url": f"https://notebook.google.com/notebook/{notebook_id}",
            "catalogFile": f"data/notebooks/{computed_slug}_catalog.json",
            "mappingFile": f"data/notebooks/{computed_slug}_mapping.json",
            "totalSources": 0,
            "lastSynced": None
        }
        registry.setdefault("notebooks", []).append(nb_entry)
    else:
        if title: nb_entry["title"] = title
        if category: nb_entry["category"] = category
        if description: nb_entry["description"] = description

    slug_val = nb_entry.get("slug", "notebook")
    catalog_path = os.path.join(BASE_DIR, nb_entry.get("catalogFile", f"data/notebooks/{slug_val}_catalog.json"))
    mapping_path = os.path.join(BASE_DIR, nb_entry.get("mappingFile", f"data/notebooks/{slug_val}_mapping.json"))

    catalog = load_json(catalog_path, {"notebookId": notebook_id, "notebookTitle": nb_entry["title"], "sources": []})
    mapping = load_json(mapping_path, {})
    
    # Recalculate dynamic live risk counters against sheets data
    sheets_path = os.path.join(SHEETS_DIR, "live_synced_data.json")
    fallback_path = os.path.join(BASE_DIR, "src", "data", "live_synced_data.json")
    chosen_path = sheets_path if os.path.exists(sheets_path) else fallback_path
    live_data = load_json(chosen_path, {"risks": [], "teamGoogleRisks": [], "issues": []})

    all_risks = live_data.get("risks", [])
    all_team_risks = live_data.get("teamGoogleRisks", [])

    for bundle_name, b_info in mapping.items():
        bundle_tag = bundle_name.lower().replace("bundle ", "")
        matched_joint = [r["id"] for r in all_risks if bundle_name.lower() in (r.get("bundle", "")).lower() or bundle_tag in (r.get("bundle", "")).lower()]
        if not matched_joint and b_info.get("jointRisks"):
            matched_joint = b_info["jointRisks"]
        b_info["jointRisks"] = list(set(matched_joint))
        b_info["activeJointRiskCount"] = len([r for r in all_risks if r["id"] in b_info["jointRisks"] and r.get("status") == "Active"])

        matched_team = [gr["id"] for gr in all_team_risks if bundle_name.lower() in (gr.get("bundle", "")).lower() or bundle_tag in (gr.get("bundle", "")).lower()]
        if not matched_team and b_info.get("teamGoogleRisks"):
            matched_team = b_info["teamGoogleRisks"]
        b_info["teamGoogleRisks"] = list(set(matched_team))
        b_info["activeTeamRiskCount"] = len([gr for gr in all_team_risks if gr["id"] in b_info["teamGoogleRisks"] and gr.get("status") == "Active"])
        b_info["totalActiveRisks"] = b_info["activeJointRiskCount"] + b_info["activeTeamRiskCount"]

    now_iso = datetime.now().isoformat()
    catalog["lastSynced"] = now_iso
    catalog["status"] = "synced"
    catalog["totalSources"] = len(catalog.get("sources", []))

    nb_entry["totalSources"] = catalog["totalSources"]
    nb_entry["lastSynced"] = now_iso
    registry["activeNotebookId"] = notebook_id

    save_json(catalog_path, catalog)
    save_json(mapping_path, mapping)
    save_json(REGISTRY_PATH, registry)

    # Also sync legacy paths for backwards compatibility
    legacy_cat = os.path.join(DATA_DIR, "notebook", "sources_catalog.json")
    legacy_map = os.path.join(DATA_DIR, "notebook", "bundle_annex_mapping.json")
    save_json(legacy_cat, catalog)
    save_json(legacy_map, mapping)

    print(f"Successfully synchronized Notebook '{nb_entry['title']}' ({catalog['totalSources']} sources).")
    return {
        "status": "ok",
        "notebook": nb_entry,
        "catalog": catalog,
        "mapping": mapping
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Notebook Sync CLI for Gemini Notebooks")
    parser.add_argument("--notebook-id", default="acdbb29b-8632-4fc7-9ba8-2357beeff141", help="Gemini Notebook UUID")
    parser.add_argument("--title", help="Notebook display title")
    parser.add_argument("--slug", help="Unique slug identifier")
    parser.add_argument("--category", help="Category (e.g. 'Contract & Governance', 'Technical Architecture')")
    parser.add_argument("--description", help="Short description")
    args = parser.parse_args()

    result = sync_notebook(args.notebook_id, args.title, args.slug, args.category, args.description)
    print(json.dumps(result, indent=2))
