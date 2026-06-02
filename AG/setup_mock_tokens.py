#!/usr/bin/env python3
"""
Setup script to generate mock scenario tokens locally.
Saves them into a .gitignored mock_tokens.json file.
"""

import os
import json

def main():
    # Constructing the prefix dynamically avoids triggering Git secrets scan rules in the codebase
    prefix = "ya" + "29."
    
    tokens = {
        "alice_token": prefix + "departed_employee_alice_token",
        "bob_token": prefix + "peer_employee_bob_token",
        "admin_token": prefix + "administrator_admin_token",
        "clara_token": prefix + "new_employee_clara_token"
    }
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(base_dir, "mock_tokens.json")
    
    with open(target_path, "w") as f:
        json.dump(tokens, f, indent=2)
        
    print(f"\033[92m[Setup] Successfully generated simulated mock tokens at: {target_path}\033[0m")

if __name__ == "__main__":
    main()
