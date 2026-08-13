#!/usr/bin/env python3
import json
import os
import sys
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NOTEBOOK_DIR = os.path.join(DATA_DIR, "notebook")
SHEETS_DIR = os.path.join(DATA_DIR, "sheets")

CATALOG_PATH = os.path.join(NOTEBOOK_DIR, "sources_catalog.json")
MAPPING_PATH = os.path.join(NOTEBOOK_DIR, "bundle_annex_mapping.json")
SHEETS_DATA_PATH = os.path.join(SHEETS_DIR, "live_synced_data.json")
FALLBACK_SHEETS_PATH = os.path.join(BASE_DIR, "src", "data", "live_synced_data.json")

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}

def sync_notebook(notebook_id="acdbb29b-8632-4fc7-9ba8-2357beeff141"):
    print(f"Starting differential sync for Gemini Notebook {notebook_id}...")
    catalog = load_json(CATALOG_PATH, {"sources": []})
    mapping = load_json(MAPPING_PATH, {})
    
    sheets_path = SHEETS_DATA_PATH if os.path.exists(SHEETS_DATA_PATH) else FALLBACK_SHEETS_PATH
    live_data = load_json(sheets_path, {"risks": [], "teamGoogleRisks": [], "issues": []})

    all_risks = live_data.get("risks", [])
    all_team_risks = live_data.get("teamGoogleRisks", [])
    all_issues = live_data.get("issues", [])

    # Recalculate dynamic live risk counters for each bundle
    for bundle_name, b_info in mapping.items():
        bundle_tag = bundle_name.lower().replace("bundle ", "")
        
        # Match joint risks by bundle or category
        matched_joint = [r["id"] for r in all_risks if bundle_name.lower() in (r.get("bundle", "")).lower() or bundle_tag in (r.get("bundle", "")).lower()]
        if not matched_joint and b_info.get("jointRisks"):
            matched_joint = b_info["jointRisks"]
        b_info["jointRisks"] = list(set(matched_joint))
        b_info["activeJointRiskCount"] = len([r for r in all_risks if r["id"] in b_info["jointRisks"] and r.get("status") == "Active"])

        # Match Team Google risks
        matched_team = [gr["id"] for gr in all_team_risks if bundle_name.lower() in (gr.get("bundle", "")).lower() or bundle_tag in (gr.get("bundle", "")).lower()]
        if not matched_team and b_info.get("teamGoogleRisks"):
            matched_team = b_info["teamGoogleRisks"]
        b_info["teamGoogleRisks"] = list(set(matched_team))
        b_info["activeTeamRiskCount"] = len([gr for gr in all_team_risks if gr["id"] in b_info["teamGoogleRisks"] and gr.get("status") == "Active"])

        b_info["totalActiveRisks"] = b_info["activeJointRiskCount"] + b_info["activeTeamRiskCount"]

    catalog["lastSynced"] = datetime.now().isoformat()
    catalog["status"] = "synced"

    os.makedirs(NOTEBOOK_DIR, exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)

    print(f"Successfully synchronized {len(catalog.get('sources', []))} sources and updated {len(mapping)} bundle mappings.")
    return {
        "status": "ok",
        "totalSources": len(catalog.get("sources", [])),
        "lastSynced": catalog["lastSynced"],
        "mapping": mapping
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Project Monaro Contract Notebook")
    parser.add_argument("--notebook-id", default="acdbb29b-8632-4fc7-9ba8-2357beeff141", help="Notebook ID")
    args = parser.parse_args()

    result = sync_notebook(args.notebook_id)
    print(json.dumps(result, indent=2))
