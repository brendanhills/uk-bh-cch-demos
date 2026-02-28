from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_policy_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "Standard Underwriting Guidelines 2026")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 65, "Effective Date: January 1, 2026 | Version 1.0")
    
    y = height - 100

    sections = [
        ("1. Credit Score Thresholds & Pricing", [
            "- Tier 1 (Preferred): 720+ Score",
            "  * Recommended Interest Rate: 6.50% Fixed",
            "  * Status: ELIGIBLE",
            "- Tier 2 (Standard): 660 - 719 Score",
            "  * Recommended Interest Rate: 8.25% Fixed",
            "  * Status: ELIGIBLE",
            "- Tier 3 (Sub-Prime): 600 - 659 Score",
            "  * Recommended Interest Rate: 12.50% Fixed",
            "  * Status: MANUAL_REVIEW required for loans > $5,000",
            "- Tier 4 (High Risk): < 600 Score",
            "  * Status: DENY immediately"
        ]),
        ("2. Debt-To-Income (DTI) Analysis", [
            "- Standard Maximum DTI: 43% (including new loan payment)",
            "- Ultra-Prime Exception: Up to 50% DTI permitted if Credit Score > 780 AND LTV < 75%",
            "- High-Leverage Warning: DTI > 40% requires verification of 6 months cash reserves"
        ]),
        ("3. Employment & Income Verification", [
            "- Minimum Tenure: 2 years (24 months) of continuous employment history required",
            "- Gaps in Employment: Any gap > 90 days requires a written explanation",
            "- Verification Methods:",
            "  * Standard: Automated 'The Work Number' or direct employer contact",
            "  * Multimodal: Pay stubs (last 2) or Bank Statements (last 3 months) for income validation",
            "- Self-Employed Applicants: Must provide 2 years of signed Federal Tax Returns"
        ]),
        ("4. Loan Purpose & Restrictions", [
            "- Permitted Purposes: Debt Consolidation, Home Improvement, Education, Major Purchase",
            "- Prohibited Purposes: Gambling, speculative trading (crypto/options), illegal activities",
            "- Restricted: Business-related loans for entities > 2 people require commercial underwriting"
        ]),
        ("5. Fraud & Identity Protection", [
            "- High Risk Flags: Immediate DENY. Examples: SSN mismatch, DOB discrepancy",
            "- Medium Risk Flags: Requires Investigator deep-dive. Example: Recent password reset",
            "- Identity Velocity: Multiple applications in 24 hours trigger automatic fraud hold"
        ]),
        ("6. High Value Loan Requirements (>$50,000)", [
            "- Strict Prohibitions: Any loan >= $50,000 is DENIED unless the following are met:",
            "  a) Verified Annual Income exceeds $150,000",
            "  b) DTI is below 35% (inclusive of the new loan)",
            "  c) Minimum of 5 years continuous employment tenure",
            "- Luxury Assets (Boats, RVs) are only permitted for Prime Tier 1 applicants"
        ])
    ]

    for title, lines in sections:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        y -= 20
        c.setFont("Helvetica", 10)
        for line in lines:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            c.drawString(70, y, line)
            y -= 15
        y -= 10

    c.save()
    print(f"Policy PDF created: {filename}")

if __name__ == "__main__":
    output_path = "loan_agent/data/policy_docs/Standard_Underwriting_Guidelines_2026.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    create_policy_pdf(output_path)
