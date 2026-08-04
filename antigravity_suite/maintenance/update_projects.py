#!/usr/bin/env python3
"""
Diagnostic and sync script for Antigravity/Gemini projects.
Ensures correct GCP Project ID configurations to prevent 'invalid project ID: ""' errors.
"""

import os
import json
import glob
import uuid
import sqlite3

# Path to Gemini/Antigravity projects directory.
# This is where the agent runner looks for the configurations associated with each folder.
PROJECTS_DIR = os.path.expanduser("~/.gemini/config/projects")
PROJECTS_JSON = os.path.expanduser("~/.gemini/projects.json")
VSCDB_PATH = os.path.expanduser("~/.config/Antigravity/User/globalStorage/state.vscdb")
APP_STORAGE_JSON = os.path.expanduser("~/.config/Antigravity/app_storage.json")

# Default settings required by the agent runner to correctly resolve
# the GCP project ID "uk-bh-experiments-argolis" and prevent the 'invalid project ID: ""' error.
DEFAULT_SETTINGS = {
    "fileAccessPolicy": "AGENT_SETTING_POLICY_ASK",
    "internetPolicy": "AGENT_SETTING_POLICY_ASK",
    "autoExecutionPolicy": "CASCADE_COMMANDS_AUTO_EXECUTION_OFF",
    "artifactReviewMode": "ARTIFACT_REVIEW_MODE_ALWAYS",
    "enterpriseGcpProjectId": "uk-bh-experiments-argolis",
    "enterpriseGcpProjectRegion": "global"
}

def load_existing_projects():
    # Scan existing projects in ~/.gemini/config/projects/*.json
    # Map each folderUri to the path of its corresponding JSON file to avoid duplicates.
    existing = {}
    search_pattern = os.path.join(PROJECTS_DIR, "*.json")
    for file_path in glob.glob(search_pattern):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            resources = data.get("projectResources", {}).get("resources", [])
            for res in resources:
                uri = res.get("folderUri", "") or res.get("gitFolder", {}).get("folderUri", "")
                if uri:
                    existing[uri.rstrip("/")] = file_path
        except Exception as e:
            print(f"Error reading existing project {file_path}: {e}")
    return existing

def get_folders_from_projects_json():
    # Extract all folders registered in ~/.gemini/projects.json
    # to ensure they have their corresponding configuration files.
    folders = {}
    if os.path.exists(PROJECTS_JSON):
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            for path, name in data.get("projects", {}).items():
                uri = f"file://{path}"
                folders[uri.rstrip("/")] = name
        except Exception as e:
            print(f"Error reading projects.json: {e}")
    return folders

def get_folders_from_vscdb():
    # Extract recently opened directories from Antigravity's SQLite database (state.vscdb)
    # to proactively cover recently opened folders.
    folders = {}
    if os.path.exists(VSCDB_PATH):
        try:
            conn = sqlite3.connect(f"file:{VSCDB_PATH}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key='history.recentlyOpenedPathsList'")
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                for entry in data.get("entries", []):
                    uri = entry.get("folderUri", "")
                    if uri:
                        name = os.path.basename(uri.rstrip("/")) or "project"
                        folders[uri.rstrip("/")] = name
            conn.close()
        except Exception as e:
            print(f"Error reading state.vscdb: {e}")
    return folders

def create_project_config(folder_uri, name):
    # Generate a new unique ID (UUID) and create a configuration JSON file.
    # This ensures that even subdirectories opened for the first time have
    # valid configurations with the correct enterpriseGcpProjectId.
    pid = str(uuid.uuid4())
    file_path = os.path.join(PROJECTS_DIR, f"{pid}.json")
    folder_path = folder_uri[7:] if folder_uri.startswith("file://") else folder_uri
    
    data = {
        "id": pid,
        "name": name,
        "projectResources": {
            "resources": [
                {
                    "folderUri": folder_uri
                }
            ]
        },
        "permissionGrants": {
            "permissionGrants": {
                "allow": [
                    "command(ls)",
                    f"read_file({folder_path})",
                    f"write_file({folder_path})",
                    "command(uv)",
                    "command(git status)",
                    "command(git add)",
                    "command(git commit)"
                ]
            }
        },
        "settings": DEFAULT_SETTINGS.copy()
    }
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Created new configuration file for {folder_uri} -> {file_path}")
        return file_path
    except Exception as e:
        print(f"Error writing configuration for {folder_uri}: {e}")
        return None

def update_app_storage(new_pids):
    # Add newly created project IDs to app_storage.json.
    # This maintains consistency of Antigravity's internal project database.
    if not new_pids:
        return
    if os.path.exists(APP_STORAGE_JSON):
        try:
            with open(APP_STORAGE_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            p_order_str = data.get("projectsOrder", "[]")
            p_order = json.loads(p_order_str)
            
            modified = False
            for pid in new_pids:
                if pid not in p_order:
                    p_order.append(pid)
                    modified = True
                    
            if modified:
                data["projectsOrder"] = json.dumps(p_order)
                with open(APP_STORAGE_JSON, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"Added {len(new_pids)} IDs to app_storage.json")
        except Exception as e:
            print(f"Error updating app_storage.json: {e}")

def main():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    
    # 1. Load currently configured projects.
    existing_projects = load_existing_projects()
    
    # 2. Collect candidate folders from projects.json and state.vscdb.
    candidate_folders = {}
    candidate_folders.update(get_folders_from_projects_json())
    candidate_folders.update(get_folders_from_vscdb())
    
    new_pids = []
    
    # 3. For each candidate folder, if it does not have a project JSON file, create it.
    for folder_uri, name in candidate_folders.items():
        if folder_uri not in existing_projects:
            file_path = create_project_config(folder_uri, name)
            if file_path:
                pid = os.path.splitext(os.path.basename(file_path))[0]
                new_pids.append(pid)
                existing_projects[folder_uri] = file_path
                
    # 4. Synchronize app_storage.json if necessary.
    update_app_storage(new_pids)
    
    # 5. Finally, update all existing configuration files to ensure
    # they inherit and have the correct GCP values and are up to date.
    search_pattern = os.path.join(PROJECTS_DIR, "*.json")
    for file_path in glob.glob(search_pattern):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            modified = False
            if "settings" not in data or not isinstance(data["settings"], dict):
                data["settings"] = DEFAULT_SETTINGS.copy()
                modified = True
                print(f"Adding default settings to: {os.path.basename(file_path)}")
            else:
                settings = data["settings"]
                if settings.get("enterpriseGcpProjectId") != "uk-bh-experiments-argolis":
                    settings["enterpriseGcpProjectId"] = "uk-bh-experiments-argolis"
                    modified = True
                if settings.get("enterpriseGcpProjectRegion") != "global":
                    settings["enterpriseGcpProjectRegion"] = "global"
                    modified = True
                for key, val in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = val
                        modified = True
            
            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"Corrected values in: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Error updating existing file {file_path}: {e}")

if __name__ == "__main__":
    main()
