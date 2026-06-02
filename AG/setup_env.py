#!/usr/bin/env python3
"""
Dynamic environment setup script for NotebookLM Enterprise Sandbox.
Retrieves active gcloud project details and updates the local .env automatically.
"""

import os
import subprocess
import sys

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError running command '{cmd}': {e.stderr.strip()}\033[0m", file=sys.stderr)
        return None

def main():
    print("\033[94m🤖 Resolving active Google Cloud Project details and printing access token...\033[0m")
    
    # 1. Get active project ID
    project_id = run_cmd("gcloud config get-value project")
    if not project_id:
        print("\033[91m[Error] Could not get active gcloud project. Ensure you have run 'gcloud init' or 'gcloud config set project <id>'.\033[0m")
        sys.exit(1)
    print(f"✔ Active GCP Project ID: \033[96m{project_id}\033[0m")
    
    # 2. Get Project Number
    project_number = run_cmd(f"gcloud projects describe {project_id} --format='value(projectNumber)'")
    if not project_number:
        print("\033[91m[Error] Failed to describe project. Ensure you are logged in and authorized in gcloud.\033[0m")
        sys.exit(1)
    print(f"✔ Resolved GCP Project Number: \033[96m{project_number}\033[0m")
    
    # 3. Get OAuth2 Access Token
    token = run_cmd("gcloud auth print-access-token")
    if not token:
        print("\033[91m[Error] Failed to print access token. Ensure you have run 'gcloud auth login' first.\033[0m")
        sys.exit(1)
    print("✔ Retrieved OAuth2 Access Token successfully.")
    
    # 4. Read / Update .env file
    env_path = ".env"
    env_example_path = ".env.example"
    
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            print(f"Copying {env_example_path} to {env_path}...")
            with open(env_example_path, "r") as f:
                content = f.read()
        else:
            content = ""
    else:
        with open(env_path, "r") as f:
            content = f.read()
            
    # Parse lines and update/replace values
    lines = content.splitlines()
    new_lines = []
    
    keys_updated = {"GCP_PROJECT_NUMBER": False, "GCP_ACCESS_TOKEN": False, "DEFAULT_MODE": False}
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("GCP_PROJECT_NUMBER="):
            new_lines.append(f"GCP_PROJECT_NUMBER={project_number}")
            keys_updated["GCP_PROJECT_NUMBER"] = True
        elif stripped.startswith("GCP_ACCESS_TOKEN="):
            new_lines.append(f"GCP_ACCESS_TOKEN={token}")
            keys_updated["GCP_ACCESS_TOKEN"] = True
        elif stripped.startswith("DEFAULT_MODE="):
            new_lines.append("DEFAULT_MODE=live")
            keys_updated["DEFAULT_MODE"] = True
        else:
            new_lines.append(line)
            
    # Add any missing keys
    if not keys_updated["GCP_PROJECT_NUMBER"]:
        new_lines.append(f"GCP_PROJECT_NUMBER={project_number}")
    if not keys_updated["GCP_ACCESS_TOKEN"]:
        new_lines.append(f"GCP_ACCESS_TOKEN={token}")
    if not keys_updated["DEFAULT_MODE"]:
        new_lines.append("DEFAULT_MODE=live")
        
    with open(env_path, "w") as f:
        f.write("\n".join(new_lines) + "\n")
        
    print(f"\n\033[92m✔ Successfully updated {env_path} for LIVE mode testing!\033[0m")
    print(f"  - GCP_PROJECT_NUMBER is set to: \033[96m{project_number}\033[0m")
    print(f"  - DEFAULT_MODE is set to: \033[96mlive\033[0m")
    print(f"  - GCP_ACCESS_TOKEN has been loaded.")

if __name__ == "__main__":
    main()
