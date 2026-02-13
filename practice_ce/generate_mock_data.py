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
            "content": "Employees are strictly prohibited from trading on material non-public information.",
            "effectiveDate": "2020-01-01",
            "acl": ["Trader", "Compliance", "HR", "Manager"]  # Public internal doc
        },
        {
            "id": "TR-002",
            "title": "Personal Account Dealing",
            "content": "All trades in personal accounts must be pre-cleared by the compliance department.",
            "effectiveDate": "2021-06-15",
            "acl": ["Trader", "Compliance", "Manager"]
        },
        {
            "id": "TR-003",
            "title": "Communications Policy",
            "content": "Use of unauthorized messaging apps (e.g. WhatsApp) for business purposes is strictly forbidden.",
            "effectiveDate": "2022-09-01",
            "acl": ["Trader", "Compliance", "HR", "Manager"]
        },
        {
            "id": "TR-004",
            "title": "Volcker Rule Constraints - Proprietary Trading",
            "content": "In accordance with the Dodd-Frank Act, CEBank International is strictly prohibited from engaging in proprietary trading or using own capital for short-term market speculation.",
            "effectiveDate": "2015-07-21",
            "acl": ["Trader", "Compliance", "Manager", "Executive"]
        },
        {
            "id": "TR-005",
            "title": "MiFID II - Best Execution Policy",
            "content": "All execution desks must take all sufficient steps to obtain the best possible result for clients, factoring in price, costs, speed, and likelihood of execution and settlement.",
            "effectiveDate": "2018-01-03",
            "acl": ["Trader", "Compliance", "Manager"]
        },
        {
            "id": "TR-006",
            "title": "Information Barriers (Chinese Walls)",
            "content": "Strict physical and digital barriers must be maintained between the Private Side (M&A, Advisory) and the Public Side (Sales, Trading, Research) to prevent the leakage of Material Non-Public Information (MNPI).",
            "effectiveDate": "2010-11-01",
            "acl": ["Trader", "Compliance", "HR", "Manager", "Executive"]
        },
        {
            "id": "TR-007",
            "title": "Prohibition of Market Manipulation",
            "content": "Engagement in any practice that artificially distorts market prices or volumes is forbidden. This includes Spoofing (placing intent-to-cancel orders), Layering, and Wash Trading.",
            "effectiveDate": "2019-04-15",
            "acl": ["Trader", "Compliance", "Manager"]
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
            "summary": "Quarterly report detailing Anti-Money Laundering monitoring activities.",
            "acl": ["Compliance", "Auditor", "Executive"]  # Traders cannot see this
        },
        {
            "id": "RF-2024-01",
            "title": "Suspicious Activity Report (SAR) - TRD-998",
            "filingDate": "2024-02-10",
            "regulator": "FinCEN",
            "status": "Review",
            "summary": "Investigation into unusual trading patterns by desk alpha.",
            "acl": ["Compliance", "Executive"] 
        },
        {
            "id": "HR-2024-DISC",
            "title": "Disciplinary Action Report - Trader X",
            "filingDate": "2024-02-12",
            "regulator": "Internal",
            "status": "Closed",
            "summary": "HR disciplinary record regarding unauthorized communications.",
            "acl": ["HR", "Executive"] # COMPLIANCE CANNOT SEE THIS (demonstrating the specific requirement)
        },
        {
            "id": "RF-COREP-2024-Q1",
            "title": "FCA COREP (Common Reporting) - Capital Adequacy",
            "filingDate": "2024-04-30",
            "regulator": "FCA / PRA",
            "status": "Submitted",
            "summary": "Standardized reporting detailing Tier 1 capital ratios, risk-weighted assets, and leverage ratios under the Capital Requirements Regulation (CRR).",
            "acl": ["Compliance", "Auditor", "Executive"]
        },
        {
            "id": "RF-10K-2023",
            "title": "SEC Form 10-K Annual Report (2023)",
            "filingDate": "2024-03-01",
            "regulator": "SEC",
            "status": "Published",
            "summary": "Comprehensive annual financial performance report, including Regulation S-K Item 1400 disclosures on Net Interest Margin and Loan Portfolio Composition.",
            "acl": ["Compliance", "Auditor", "Executive", "Trader", "HR"] # Public filing
        },
        {
            "id": "RF-FFIEC-031-2024",
            "title": "FFIEC Call Report - Consolidated",
            "filingDate": "2024-04-15",
            "regulator": "FDIC",
            "status": "Submitted",
            "summary": "Quarterly report assessing the bank's health based on the CAMELS rating system (Capital, Assets, Management, Earnings, Liquidity, Sensitivity).",
            "acl": ["Compliance", "Auditor", "Executive"]
        },
        {
            "id": "RF-SAR-994",
            "title": "Suspicious Activity Report (SAR) - Client Alpha",
            "filingDate": "2024-02-28",
            "regulator": "FinCEN",
            "status": "Submitted",
            "summary": "Confidential report detailing structured cash deposits indicative of potential money laundering by retail client.",
            "acl": ["Compliance", "Executive"] # Highly restricted
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
            "acl": ["Compliance", "Auditor", user.split(" ")[0]] # Admin/Compliance, or the user themselves
        })
        
    # Inject specific test case logs for demo (Trading Violations)
    violation_logs = [
        {
            "id": "AUD-9901",
            "timestamp": (base_date + timedelta(days=15)).isoformat(),
            "userId": "tim.trader",
            "action": "COMMUNICATION_FLAGGED",
            "details": "WhatsApp usage detected matching restricted keyword 'guaranteed return'. Trading violation.",
            "acl": ["Compliance", "Auditor"]
        },
        {
            "id": "AUD-9902",
            "timestamp": (base_date + timedelta(days=15, hours=1)).isoformat(),
            "userId": "system",
            "action": "ACCOUNT_LOCKED",
            "details": "Account tim.trader locked pending trading violation investigation.",
            "acl": ["Compliance", "Auditor", "HR"]
        },
         {
            "id": "AUD-9903",
            "timestamp": (base_date + timedelta(days=16)).isoformat(),
            "userId": "cathy.compliance",
            "action": "DOCUMENT_READ",
            "details": "Accessed TR-003 during trading violation investigation.",
            "acl": ["Compliance", "Auditor"]
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
            {"username": "catherine.ceo", "password": "password123", "role": "Executive"}
        ]
    }

    os.makedirs("data", exist_ok=True)
    with open("data/mock_db.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Mock data generated successfully at data/mock_db.json")

if __name__ == "__main__":
    generate_mock_data()
