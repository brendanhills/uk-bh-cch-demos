#!/usr/bin/env python3
"""
Authorization and Environment Setup Script for NotebookLM Enterprise Sandbox.
Runs 'gcloud auth login --enable-gdrive-access', retrieves the token, prints it, and updates/adds it to .env.
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
    print("\033[95m========================================================================\033[0m")
    print("\033[95m🔐 NotebookLM Enterprise Sandbox - Interactive Authorization\033[0m")
    print("\033[95m========================================================================\033[0m")
    
    # 1. Start the interactive authorization process
    print("\n\033[94m🔄 Launching 'gcloud auth login --enable-gdrive-access'...\033[0m")
    print("👉 Please follow the prompts in your browser to authorize your account.")
    try:
        # We run this interactively so the user can see and complete the browser OAuth flow
        subprocess.run(["gcloud", "auth", "login", "--enable-gdrive-access"], check=True)
        print("\033[92m✔ Authorization flow completed successfully!\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\n\033[91m❌ [Error] gcloud auth login failed or was cancelled: {e}\033[0m", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("\n\033[91m❌ [Error] 'gcloud' CLI is not installed or not in PATH.\033[0m", file=sys.stderr)
        sys.exit(1)

    # 2. Retrieve the OAuth2 Access Token
    print("\n\033[94m🔑 Retrieving Google Cloud OAuth2 Access Token...\033[0m")
    token = run_cmd("gcloud auth print-access-token")
    if not token:
        print("\033[91m❌ [Error] Failed to print access token.\033[0m", file=sys.stderr)
        sys.exit(1)
        
    print("\n\033[92m✔ Retrieve token successfully!\033[0m")
    print("\033[93m========================================= ACCESS TOKEN =========================================\033[0m")
    print(f"\033[96m{token}\033[0m")
    print("\033[93m================================================================================================\033[0m")

    # 3. Resolve GCP Project Details (ID and Numeric Project Number)
    print("\n\033[94m🔍 Resolving active GCP Project details...\033[0m")
    project_id = run_cmd("gcloud config get-value project")
    project_number = None
    if project_id:
        print(f"✔ Active GCP Project ID: \033[96m{project_id}\033[0m")
        project_number = run_cmd(f"gcloud projects describe {project_id} --format='value(projectNumber)'")
        if project_number:
            print(f"✔ Resolved GCP Project Number: \033[96m{project_number}\033[0m")
        else:
            print("\033[33m⚠️  Warning: Could not resolve numeric Project Number. Will skip updating GCP_PROJECT_NUMBER.\033[0m")
    else:
        print("\033[33m⚠️  Warning: Active gcloud project ID is not set. Will skip updating GCP_PROJECT_NUMBER.\033[0m")

    # 4. Load/Create .env file
    env_path = ".env"
    env_example_path = ".env.example"
    
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            print(f"\n📂 Creating new {env_path} by copying {env_example_path}...")
            with open(env_example_path, "r") as f:
                content = f.read()
        else:
            print(f"\n📂 Creating empty {env_path}...")
            content = ""
    else:
        print(f"\n📂 Reading existing {env_path} file...")
        with open(env_path, "r") as f:
            content = f.read()

    # 5. Parse and Update/Add keys
    lines = content.splitlines()
    new_lines = []
    
    keys_updated = {
        "GCP_PROJECT_NUMBER": False,
        "GCP_ACCESS_TOKEN": False,
        "DEFAULT_MODE": False
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("GCP_PROJECT_NUMBER="):
            if project_number:
                new_lines.append(f"GCP_PROJECT_NUMBER={project_number}")
                keys_updated["GCP_PROJECT_NUMBER"] = True
            else:
                new_lines.append(line)
        elif stripped.startswith("GCP_ACCESS_TOKEN="):
            new_lines.append(f"GCP_ACCESS_TOKEN={token}")
            keys_updated["GCP_ACCESS_TOKEN"] = True
        elif stripped.startswith("DEFAULT_MODE="):
            new_lines.append("DEFAULT_MODE=live")
            keys_updated["DEFAULT_MODE"] = True
        else:
            new_lines.append(line)
            
    # Add any keys that were not already in .env
    if project_number and not keys_updated["GCP_PROJECT_NUMBER"]:
        new_lines.append(f"GCP_PROJECT_NUMBER={project_number}")
        keys_updated["GCP_PROJECT_NUMBER"] = True
        
    if not keys_updated["GCP_ACCESS_TOKEN"]:
        new_lines.append(f"GCP_ACCESS_TOKEN={token}")
        keys_updated["GCP_ACCESS_TOKEN"] = True
        
    if not keys_updated["DEFAULT_MODE"]:
        new_lines.append("DEFAULT_MODE=live")
        keys_updated["DEFAULT_MODE"] = True

    # 6. Write updated content to .env
    with open(env_path, "w") as f:
        f.write("\n".join(new_lines) + "\n")
        
    print(f"\n\033[92m✔ Successfully updated {env_path} with your active credentials!\033[0m")
    if project_number:
        print(f"  - GCP_PROJECT_NUMBER is set to: \033[96m{project_number}\033[0m")
    print(f"  - GCP_ACCESS_TOKEN is loaded.")
    print(f"  - DEFAULT_MODE is set to: \033[96mlive\033[0m")
    print("\n🚀 You are now ready to run Live Mode tests or individual scripts!")

if __name__ == "__main__":
    main()
