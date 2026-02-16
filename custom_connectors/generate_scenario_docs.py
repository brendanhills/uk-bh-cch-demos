import os
import json
import shutil
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# Configuration for Scenarios
BASE_DIR = "drive_content"

SCENARIOS = {
    "Scenario_1_Trading_Policies": {
        "subfolders": {
            "Shared_Trading_Policies": {
                 "files": [
                    {
                        "filename": "Global_Trading_Gifts_Policy.pdf",
                        "title": "Global Trading & Gifts Policy",
                        "content": """
                        1. Purpose
                        This policy establishes the standards for giving and receiving gifts and entertainment for all Trading personnel.

                        2. Scope
                        Applies to all employees in the Global Markets division.

                        3. General Rules
                        - Gifts > $100 must be reported.
                        - Gifts > $500 require pre-approval.
                        - No gifts to government officials.
                        
                        4. Trading Specifics
                        Traders are strictly prohibited from accepting gifts from active counterparties during settlement periods.
                        """,
                        "confidentiality": "INTERNAL"
                    }
                ],
                 "permissions": {
                    "description": "Visible to Traders, IB, and Compliance.",
                    "access_rules": [
                        {"file_pattern": "*", "roles": ["Traders", "InvestmentBanking", "ComplianceOfficers"]}
                    ]
                }
            },
            "IB_Confidential": {
                "files": [
                     {
                        "filename": "Investment_Banking_Gifts_Policy.pdf",
                        "title": "Investment Banking Gifts & Entertainment Policy",
                        "content": """
                        1. Purpose
                        Specific guidelines for Investment Banking (IB) interactions with clients.

                        2. Scope
                        Applies to Deal Teams and M&A Advisory.

                        3. Thresholds
                        - Client dinners up to $200/head allowed without pre-approval.
                        - Closing dinners: Special budget applies.
                        
                        4. Restrictions
                        No gifts during 'Quiet Periods' or active deal negotiations.
                        """,
                        "confidentiality": "INTERNAL - IB ONLY"
                    }
                ],
                 "permissions": {
                    "description": "Visible to IB and Compliance ONLY.",
                    "access_rules": [
                        {"file_pattern": "*", "roles": ["InvestmentBanking", "ComplianceOfficers"]}
                    ]
                }
            }
        },
        "permissions": {
            "description": "Trading Policies Root",
            "access_rules": []
        }
    },
    "Scenario_2_HR_Records": {
        "subfolders": {
            "John_Smith": {
                "files": [
                    {
                        "filename": "Termination_Process_John_Smith.pdf",
                        "title": "Termination Checklist - John Smith",
                        "content": """
                        Employee: John Smith
                        ID: E-99281
                        Date: 2026-02-15

                        1. Exit Interview Completed: Yes
                        2. Laptop Returned: Pending
                        3. Badge Deactivated: Yes
                        4. Severance Package: Standard Plan B
                        
                        Reason: Restructuring / Redundancy.
                        """,
                        "confidentiality": "CONFIDENTIAL - HR EYES ONLY"
                    },
                     {
                        "filename": "Performance_Review_John_Smith_2025.pdf",
                        "title": "2025 Performance Review - John Smith",
                        "content": """
                        Rating: 3/5 (Meets Expectations)
                        
                        Strengths: 
                        - Good technical skills
                        - Reliable attendance
                        
                        Areas for Improvement:
                        - Communication with stakeholders
                        - Need to be more proactive in team meetings
                        
                        Manager: Harry HR
                        """,
                        "confidentiality": "CONFIDENTIAL - HR EYES ONLY"
                    }
                ],
                "permissions": {
                     "description": "Restricted to HR Managers and John's direct manager.",
                     "access_rules": [
                         {"file_pattern": "*", "users": ["harry.hr", "hannah.hr"]} # Assuming harry is the manager
                     ]
                }
            }
        },
        "permissions": { # Folder level defaults
             "description": "HR Root Folder",
             "access_rules": [
                 {"file_pattern": "*", "users": ["harry.hr"]}
             ]
        }
    },
    "Scenario_3_Compliance_Audits": {
        "files": [
             {
                "filename": "Audit_Log_Trading_Violations_Q1.pdf",
                "title": "Q1 2026 Trading Violations Audit",
                "content": """
                CONFIDENTIAL AUDIT LOG
                
                Incident #1:
                Date: 2026-01-15
                Trader involved: Tim Trader
                Violation: Exceeded position limit on VOD.L
                Action: Warning issued.

                Incident #2:
                Date: 2026-02-02
                Trader involved: Unknown
                Violation: Unmapped trade routed to dark pool.
                Action: System patch applied.
                """,
                "confidentiality": "RESTRICTED - COMPLIANCE ONLY"
            }
        ],
        "permissions": {
             "description": "Accessible to Compliance Officers.",
             "access_rules": [
                 {"file_pattern": "*", "users": ["cathy.compliance", "colin.compliance"]}
             ]
        }
    },
    "Scenario_4_IT_Support": {
        "subfolders": {
            "General_Knowledge_Base": {
                "files": [
                    {
                        "filename": "KB_Password_Reset_Instructions.pdf",
                        "title": "How to Reset Your Domain Password",
                        "content": """
                        ServiceNow Article KB00123
                        
                        1. Go to https://password.internal
                        2. Enter your username.
                        3. Complete MFA challenge.
                        4. Enter new password (must be 14 chars, 1 number, 1 symbol).
                        
                        Troubleshooting:
                        If locked out, call Helpdesk at x5555.
                        """,
                        "confidentiality": "INTERNAL - ALL STAFF"
                    }
                ],
                "permissions": {
                     "description": "Visible to everyone.",
                     "access_rules": [
                         {"file_pattern": "*", "groups": ["All Users"]}
                     ]
                }
            },
            "Admin_Procedures": {
                 "files": [
                    {
                        "filename": "Workday_Backend_Admin_Guide.pdf",
                        "title": "Workday Backend Admin Procedures",
                        "content": """
                        WARNING: ADMIN USE ONLY
                        
                        Root access to Workday integration layer.
                        
                        Restarting Services:
                        `sudo systemctl restart workday-connector`
                        
                        API Keys:
                        Located in Vault path: secret/production/workday/api_key
                        
                        Emergency Database Restore:
                        Use the `restore_db.sh` script in `/opt/admin/scripts`.
                        """,
                        "confidentiality": "RESTRICTED - IT ADMINS ONLY"
                    }
                ],
                "permissions": {
                     "description": "Visible to IT Admins only.",
                     "access_rules": [
                         {"file_pattern": "*", "users": ["ivan.it", "admin.alice"]}
                     ]
                }
            }
        },
        "permissions": {
            "description": "IT Support Root",
            "access_rules": [
                {"file_pattern": "*", "users": ["ivan.it"]}
            ]
        }

    }
}

def create_pdf(filepath, title, content, confidentiality):
    doc = SimpleDocTemplate(filepath, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    # Confidentiality Stamp
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        textColor=colors.red,
        alignment=1 # Center
    )
    story.append(Paragraph(f"[{confidentiality}]", header_style))
    story.append(Spacer(1, 24))

    # Content
    for line in content.strip().split('\n'):
        story.append(Paragraph(line.strip(), styles['Normal']))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"Created PDF: {filepath}")

def create_users_json(folder_path, permissions):
    filepath = os.path.join(folder_path, "users.json")
    with open(filepath, 'w') as f:
        json.dump(permissions, f, indent=2)
    print(f"Created users.json: {filepath}")

def process_scenario(base_path, scenario_data):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Process files in this directory
    if "files" in scenario_data:
        for file_data in scenario_data["files"]:
            pdf_path = os.path.join(base_path, file_data["filename"])
            create_pdf(
                pdf_path,
                file_data["title"],
                file_data["content"],
                file_data["confidentiality"]
            )
    
    # Process permissions
    if "permissions" in scenario_data:
        create_users_json(base_path, scenario_data["permissions"])

    # Process subfolders
    if "subfolders" in scenario_data:
        for folder_name, folder_data in scenario_data["subfolders"].items():
            subfolder_path = os.path.join(base_path, folder_name)
            process_scenario(subfolder_path, folder_data)

def main():
    print(f"Generating content in {BASE_DIR}...")
    
    # Clean up previous
    if os.path.exists(BASE_DIR):
        print(f"Cleaning up {BASE_DIR}...")
        shutil.rmtree(BASE_DIR)
    
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    for scenario_name, scenario_data in SCENARIOS.items():
        scenario_path = os.path.join(BASE_DIR, scenario_name)
        process_scenario(scenario_path, scenario_data)

    print("\nGeneration Complete.")

if __name__ == "__main__":
    main()
