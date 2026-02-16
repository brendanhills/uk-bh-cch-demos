import json
import os
import random
from datetime import datetime, timedelta

def generate_mock_data():
    # Roles: 
    # - Trader: General access to rules, own audit logs.
    # - Compliance: Access to rules, regulatory filings, all audit logs, but NOT HR files (demonstrating the boundary).
    # - HR: Access to HR files.
    
    # 1. Trading Rules
    trading_rules = [
        {
            "id": "TR-001",
            "title": "Insider Trading Policy",
            "content": """Employees are strictly prohibited from trading on material non-public information. This policy applies to all employees, consultants, and contractors of CEBank International. Material non-public information (MNPI) is defined as any information that has not been disclosed to the general public and could affect the market price of a security. Examples include impending mergers, earnings reports, and significant legal changes.

Violations of this policy may result in severe disciplinary action, including termination of employment and referral to regulatory authorities. All employees must certify their compliance with this policy annually. Personal trading accounts must be disclosed and are subject to monitoring to detect potential overlaps with the bank's restricted lists.""",
            "effectiveDate": "2020-01-01",
            "category": "TradingRule",
            "sensitivity": "Internal"
        },
        {
            "id": "TR-002",
            "title": "Personal Account Dealing",
            "content": """All trades in personal accounts must be pre-cleared by the compliance department. This ensures that personal trading activities do not conflict with the interests of CEBank's clients or the bank itself. Employees must submit a pre-clearance request via the internal compliance portal at least 24 hours prior to execution.

Approvals are valid for 24 hours from the time of issuance. Certain securities, such as those on the Restricted List or Watch List, will be automatically denied. Failure to obtain pre-clearance or trading after an approval has expired is a violation of the bank's Code of Conduct and may lead to disgorgements of improved profits or disciplinary action.""",
            "effectiveDate": "2021-06-15",
            "category": "TradingRule",
            "sensitivity": "Internal"
        },
        {
            "id": "TR-003",
            "title": "Communications Policy",
            "content": """Use of unauthorized messaging apps (e.g., WhatsApp, Signal, Telegram) for business purposes is strictly forbidden. All business communications must be conducted through approved channels that are captured and archived by the bank's surveillance systems. This includes email, Bloomberg Chat, and authorized internal messaging platforms.

The use of personal devices for business communication is famously known as 'off-channel communications' and has led to significant fines for financial institutions. If a client initiates contact via an unapproved channel, employees must immediately redirect the conversation to an approved channel and report the interaction to Compliance to ensure a complete audit trail.""",
            "effectiveDate": "2022-09-01",
            "category": "TradingRule",
            "sensitivity": "Internal"
        },
        {
            "id": "TR-004",
            "title": "Volcker Rule Constraints - Proprietary Trading",
            "content": """In accordance with the Dodd-Frank Act, CEBank International is strictly prohibited from engaging in proprietary trading or using own capital for short-term market speculation. The Volcker Rule aims to protect bank customers by preventing banks from making certain types of speculative investments that contributed to the 2008 financial crisis.

This policy outlines the specific exemptions allowed under the rule, such as market making, underwriting, and risk-mitigating hedging. Each desk must maintain a comprehensive inventory of its positions and demonstrate that they are within the limits set for market-making activities. Independent testing will be conducted annually to ensure ongoing compliance with these strict regulations.""",
            "effectiveDate": "2015-07-21",
            "category": "TradingRule",
            "sensitivity": "Restricted"
        },
        {
            "id": "TR-005",
            "title": "MiFID II - Best Execution Policy",
            "content": """All execution desks must take all sufficient steps to obtain the best possible result for clients, factoring in price, costs, speed, and likelihood of execution and settlement. This 'Best Execution' obligation applies to all asset classes and requires the bank to have a written execution policy that is reviewed at least annually.

Traders must evaluate execution venues based on quantitative and qualitative factors. In the event of a material change in market conditions allowing for better execution on a new venue, the policy must be updated accordingly. Reports on the top five execution venues (RTS 28) must be published annually to demonstrate transparency to clients.""",
            "effectiveDate": "2018-01-03",
            "category": "TradingRule",
            "sensitivity": "Internal"
        },
        {
            "id": "TR-006",
            "title": "Information Barriers (Chinese Walls)",
            "content": """Strict physical and digital barriers must be maintained between the Private Side (M&A, Advisory) and the Public Side (Sales, Trading, Research) to prevent the leakage of Material Non-Public Information (MNPI). These 'Chinese Walls' are essential for managing conflicts of interest and ensuring fair markets.

Employees on the Private Side are 'over the wall' and possess confidential information. They must not communicate this information to Public Side employees unless a specific 'wall-crossing' procedure is followed, which requires Compliance approval and logging. Physical access to Private Side floors is restricted to authorized personnel only, and digital access controls prevent unauthorized data sharing.""",
            "effectiveDate": "2010-11-01",
            "category": "TradingRule",
            "sensitivity": "Restricted"
        },
        {
            "id": "TR-007",
            "title": "Prohibition of Market Manipulation",
            "content": """Engagement in any practice that artificially distorts market prices or volumes is forbidden. This includes Spoofing (placing intent-to-cancel orders), Layering (creating a false impression of liquidity), and Wash Trading (buying and selling the same instrument to create volume).

Algorithmic trading strategies must be tested to ensure they do not contribute to disorderly market conditions. Traders are responsible for monitoring their orders and must report any suspicious activity observed in the market. The bank utilizes automated surveillance tools to detect potential manipulative patterns and will investigate all triggered alerts.""",
            "effectiveDate": "2019-04-15",
            "category": "TradingRule",
            "sensitivity": "Internal"
        }
    ]

    # 2. Regulatory Filings (More restricted)
    regulatory_filings = [
        {
            "id": "RF-2023-Q4",
            "title": "Q4 2023 AML Compliance Report",
            "filingDate": "2024-01-15",
            "regulator": "FCA",
            "status": "Submitted",
            "summary": """Quarterly report detailing Anti-Money Laundering monitoring activities. This report summarizes the alerts generated by the transaction monitoring system, the number of Suspicious Activity Reports (SARs) filed, and the outcome of enhanced due diligence (EDD) reviews.

It also highlights key risks identified during the quarter, such as increased activity in high-risk jurisdictions or emergence of new typologies. The report includes metrics on the timeliness of alert disposition and the quality of investigations conducted by the AML team.""",
            "category": "RegulatoryFiling",
            "sensitivity": "Confidential"
        },
        {
            "id": "RF-2024-01",
            "title": "Suspicious Activity Report (SAR) - TRD-998",
            "filingDate": "2024-02-10",
            "regulator": "FinCEN",
            "status": "Review",
            "summary": """Investigation into unusual trading patterns by desk alpha. This Suspicious Activity Report (SAR) documents a series of trades executed on February 10, 2024, involving a large position in XYZ Corp just before a positive earnings announcement.

The trader in question, 'Trader A', had no prior history of trading this specific equity. The timing and size of the trade suggest potential knowledge of MNPI. The account has been placed under heightened supervision, and this report is filed with FinCEN in accordance with the Bank Secrecy Act.""",
            "category": "RegulatoryFiling",
            "sensitivity": "Restricted"
        },
        {
            "id": "HR-2024-DISC",
            "title": "Disciplinary Action Report - Trader X",
            "filingDate": "2024-02-12",
            "regulator": "Internal",
            "status": "Closed",
            "summary": """HR disciplinary record regarding unauthorized communications. Employee 'Trader X' was found to be using WhatsApp to communicate with three hedge fund clients regarding market color and pricing. This is a direct violation of the Communications Policy (TR-003).

The employee has been issued a formal written warning and their bonus for the current year is subject to clawback provisions. Mandatory training on communication compliance has been assigned and must be completed within 30 days. Further violations will result in termination.""",
            "category": "HRRecord",
            "sensitivity": "Confidential"
        },
        {
            "id": "RF-COREP-2024-Q1",
            "title": "FCA COREP (Common Reporting) - Capital Adequacy",
            "filingDate": "2024-04-30",
            "regulator": "FCA / PRA",
            "status": "Submitted",
            "summary": """Standardized reporting detailing Tier 1 capital ratios, risk-weighted assets, and leverage ratios under the Capital Requirements Regulation (CRR). This dataset is critical for the regulator to assess the bank's solvency and resilience to stress.

The report covers credit risk, market risk, and operational risk components. Significant changes from the previous quarter include an increase in RWA due to a new model validation adjustment for the equity trading desk. The current CET1 ratio stands at 14.5%, well above the regulatory minimum.""",
            "category": "RegulatoryFiling",
            "sensitivity": "Confidential"
        },
        {
            "id": "RF-10K-2023",
            "title": "SEC Form 10-K Annual Report (2023)",
            "filingDate": "2024-03-01",
            "regulator": "SEC",
            "status": "Published",
            "summary": """Comprehensive annual financial performance report, including Regulation S-K Item 1400 disclosures on Net Interest Margin and Loan Portfolio Composition. This document provides a detailed overview of CEBank International's financial health, business strategy, and risk factors.

Key sections include Management's Discussion and Analysis (MD&A), audited financial statements, and notes to the accounts. It also discloses legal proceedings, executive compensation, and market risk disclosures. This public filing is available to all investors and stakeholders.""",
            "category": "RegulatoryFiling",
            "sensitivity": "Public"
        },
        {
            "id": "RF-FFIEC-031-2024",
            "title": "FFIEC Call Report - Consolidated",
            "filingDate": "2024-04-15",
            "regulator": "FDIC",
            "status": "Submitted",
            "summary": """Quarterly report assessing the bank's health based on the CAMELS rating system (Capital, Assets, Management, Earnings, Liquidity, Sensitivity). This consolidated report aggregates data from all domestic and foreign offices of CEBank.

It provides granular data on loan performance, allowance for credit losses (ACL), and deposit insurance assessments. The data is used by the FDIC to calculate deposit insurance premiums and monitor systemic risk.""",
            "category": "RegulatoryFiling",
            "sensitivity": "Confidential"
        },
        {
            "id": "RF-SAR-994",
            "title": "Suspicious Activity Report (SAR) - Client Alpha",
            "filingDate": "2024-02-28",
            "regulator": "FinCEN",
            "status": "Submitted",
            "summary": """Confidential report detailing structured cash deposits indicative of potential money laundering by retail client. The client, 'Client Alpha', made 14 cash deposits of $9,500 over a two-week period at different branch locations.

This pattern, known as 'structuring' or 'smurfing', is designed to evade the $10,000 Currency Transaction Report (CTR) filing threshold. The source of funds could not be verified, and the client's stated occupation does not support this volume of cash. We recommend account closure.""",
            "category": "RegulatoryFiling",
            "sensitivity": "Restricted"
        }
    ]

    # 3. Audit Logs (Generated dynamically to show history)
    audit_logs = []
    actions = ["LOGIN_SUCCESS", "LOGIN_FAILED", "DOCUMENT_READ", "TRADE_PRECLEARANCE_SUBMITTED", "TRADE_PRECLEARANCE_APPROVED", "UNAUTHORIZED_ACCESS_ATTEMPT", "COMMUNICATION_FLAGGED"]
    users = ["tim.trader (Trader)", "tina.trader (Trader)", "cathy.compliance (Compliance)", "helen.hr (HR)", "system"]
    
    # Specific incident logs for the demo (Trading violation search)
    base_date = datetime.now() - timedelta(days=30)
    
    # Generate some random standard logs
    for i in range(100):
        log_date = base_date + timedelta(days=random.randint(0, 28), hours=random.randint(0, 23))
        user = random.choice(users)
        action = random.choice(actions)
        details = f"Action {action} performed successfully."
        
        audit_logs.append({
            "id": f"AUD-{1000+i}",
            "timestamp": log_date.isoformat(),
            "userId": user.split(" ")[0],
            "action": action,
            "details": details,
            "category": "AuditLog",
            "sensitivity": "Confidential"
        })
        
    # Inject specific test case logs for demo (Trading Violations)
    violation_logs = [
        {
            "id": "AUD-9901",
            "timestamp": (base_date + timedelta(days=15)).isoformat(),
            "userId": "tim.trader",
            "action": "COMMUNICATION_FLAGGED",
            "details": "WhatsApp usage detected matching restricted keyword 'guaranteed return'. Trading violation.",
            "category": "AuditLog",
            "sensitivity": "Confidential"
        },
        {
            "id": "AUD-9902",
            "timestamp": (base_date + timedelta(days=15, hours=1)).isoformat(),
            "userId": "system",
            "action": "ACCOUNT_LOCKED",
            "details": "Account tim.trader locked pending trading violation investigation.",
            "category": "AuditLog",
            "sensitivity": "Restricted"
        },
         {
            "id": "AUD-9903",
            "timestamp": (base_date + timedelta(days=16)).isoformat(),
            "userId": "cathy.compliance",
            "action": "DOCUMENT_READ",
            "details": "Accessed TR-003 during trading violation investigation.",
            "category": "AuditLog",
            "sensitivity": "Confidential"
        }
    ]
    audit_logs.extend(violation_logs)
    
    # Sort logs by timestamp
    audit_logs.sort(key=lambda x: x["timestamp"])

    data = {
        "trading_rules": trading_rules,
        "regulatory_filings": regulatory_filings,
        "audit_logs": audit_logs,
        "users": [
            # Traders
            {"username": "tim.trader", "password": "password123", "role": "Trader"},
            {"username": "tina.trader", "password": "password123", "role": "Trader"},
            {"username": "tom.trader", "password": "password123", "role": "Trader"},
            # Compliance
            {"username": "cathy.compliance", "password": "password123", "role": "Compliance"},
            {"username": "caleb.compliance", "password": "password123", "role": "Compliance"},
            {"username": "chloe.compmgr", "password": "password123", "role": "Compliance"},
            # HR
            {"username": "helen.hr", "password": "password123", "role": "HR"},
            {"username": "harry.hr", "password": "password123", "role": "HR"},
            # Investment Banking
            {"username": "ian.ibanker", "password": "password123", "role": "InvestmentBanking"},
            {"username": "iona.ibanker", "password": "password123", "role": "InvestmentBanking"},
            # Auditors
            {"username": "annie.auditor", "password": "password123", "role": "Auditor"},
            {"username": "arthur.auditorext", "password": "password123", "role": "Auditor"},
            # Executives
            {"username": "edward.exec", "password": "password123", "role": "Executive"},
            {"username": "catherine.ceo", "password": "password123", "role": "Executive"},
            # Special connector user for Gemini Enterprise
            {"username": "gemini.connector", "password": "password123", "role": "Connector"}
        ]
    }

    os.makedirs("data", exist_ok=True)
    
    # Save users
    with open("data/users.json", "w") as f:
        json.dump(data["users"], f, indent=4)
        
    # Save trading rules
    with open("data/trading_rules.json", "w") as f:
        json.dump(data["trading_rules"], f, indent=4)
        
    # Save regulatory filings
    with open("data/regulatory_filings.json", "w") as f:
        json.dump(data["regulatory_filings"], f, indent=4)
        
    # Save audit logs
    with open("data/audit_logs.json", "w") as f:
        json.dump(data["audit_logs"], f, indent=4)
        
    # Save ACLs (Policy Definition)
    # Policy: Role -> Permissions (List of allowed {Category, MaxSensitivity})
    # Hierarchical Sensitivity: Public < Internal < Confidential < Restricted
    acls = {
        "roles": {
            "Trader": {
                "permissions": [
                    {"category": "TradingRule", "max_sensitivity": "Internal"},
                    {"category": "RegulatoryFiling", "max_sensitivity": "Public"},
                    {"category": "HRRecord", "max_sensitivity": "Public"} 
                ]
            },
            "Compliance": {
                "permissions": [
                    {"category": "TradingRule", "max_sensitivity": "Restricted"},
                    {"category": "RegulatoryFiling", "max_sensitivity": "Restricted"},
                    {"category": "AuditLog", "max_sensitivity": "Restricted"},
                    {"category": "HRRecord", "max_sensitivity": "Internal"}
                ]
            },
            "HR": {
                "permissions": [
                    {"category": "TradingRule", "max_sensitivity": "Internal"},
                    {"category": "HRRecord", "max_sensitivity": "Confidential"}
                ]
            },
            "Executive": {
                "permissions": [
                    {"category": "TradingRule", "max_sensitivity": "Restricted"},
                    {"category": "RegulatoryFiling", "max_sensitivity": "Restricted"},
                    {"category": "AuditLog", "max_sensitivity": "Restricted"},
                    {"category": "HRRecord", "max_sensitivity": "Restricted"}
                ]
            },
            "Auditor": {
                "permissions": [
                    {"category": "TradingRule", "max_sensitivity": "Internal"},
                    {"category": "RegulatoryFiling", "max_sensitivity": "Confidential"},
                    {"category": "AuditLog", "max_sensitivity": "Confidential"}
                ]
            },
             "InvestmentBanking": {
                "permissions": [
                    {"category": "TradingRule", "max_sensitivity": "Restricted"}, # Needs to see Chinese Wall policies
                    {"category": "RegulatoryFiling", "max_sensitivity": "Internal"}
                ]
            }
        },
        "sensitivity_levels": {
            "Public": 0,
            "Internal": 1,
            "Confidential": 2,
            "Restricted": 3
        }
    }
    with open("data/acls.json", "w") as f:
        json.dump(acls, f, indent=4)
        
    print("Mock data generated successfully in data/ directory.")

if __name__ == "__main__":
    generate_mock_data()
