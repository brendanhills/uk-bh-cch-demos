from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def create_policy_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    def draw_header(canvas_obj, page_num):
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawCentredString(width/2, height - 50, "Global Retail Lending: Standard Underwriting Guidelines 2026")
        canvas_obj.setFont("Helvetica-Oblique", 8)
        canvas_obj.drawCentredString(width/2, height - 65, f"Internal Use Only - Confidential | Version 2.0.4 | Page {page_num}")
        canvas_obj.line(50, height - 70, width - 50, height - 70)

    page_num = 1
    draw_header(c, page_num)
    
    y = height - 100

    content = [
        ("PREAMBLE & REGULATORY COMPLIANCE", [
            "This document establishes the binding framework for credit risk assessment within the retail lending division.",
            "All underwriting actions must strictly adhere to the Equal Credit Opportunity Act (ECOA), Regulation B,",
            "and the Fair Credit Reporting Act (FCRA). Unauthorized deviation from these mandates is strictly prohibited.",
            "The 2026 guidelines emphasize algorithmic objectivity and data-driven grounding for every decision."
        ]),
        ("SECTION 1: HIGH-VALUE LOAN MANDATES (MANDATORY)", [
            "Notwithstanding any other provision in this document, the following mandates apply to high-value requests.",
            "- DEFINITION: Any loan request with a Principal Amount of USD 50000 or greater.",
            "- MANDATORY REQUIREMENT A: Applicant Annual Income MUST exceed USD 150000.",
            "- MANDATORY REQUIREMENT B: Projected Debt-to-Income (DTI) ratio MUST be below 35 PERCENT.",
            "- ADJUDICATION: If BOTH Requirement A and Requirement B are not satisfied, the application MUST be DENIED.",
            "- DELEGATED AUTHORITY: High-value approvals cannot be overridden by Junior Underwriters."
        ]),
        ("SECTION 2: CREDIT SCORE TIERS & RISK-BASED PRICING", [
            "Adherence to the following tiers is mandatory for all standard-path applications:",
            "- TIER 1 (720 to 850): ELIGIBLE. Primary Interest Rate is 6.50 PERCENT fixed per annum.",
            "- TIER 2 (660 to 719): ELIGIBLE. Adjusted Interest Rate is 8.25 PERCENT fixed per annum.",
            "- TIER 3 (600 to 659): CONDITIONAL. Action: MANUAL REVIEW REQUIRED. Escalate to Senior Underwriter.",
            "- TIER 4 (Below 600): INELIGIBLE. Action: DENY. No counter-offers permitted for Tier 4 profiles."
        ]),
        ("SECTION 3: QUANTITATIVE DEBT-TO-INCOME (DTI) LIMITS", [
            "The calculation of the Projected DTI must include the proposed monthly debt obligation of the new facility.",
            "- Standard DTI Ceiling: 43 PERCENT for all unsecured retail lending products.",
            "- High-Leverage Warning: Any DTI exceeding 40 PERCENT requires verification of 6 months liquid cash reserves.",
            "- Absolute Ceiling: No loan shall be approved with a Projected DTI exceeding 50 PERCENT.",
            "- DTI DISCREPANCIES: Any variance > 5% between stated and verified debt triggers an automatic manual hold."
        ]),
        ("SECTION 4: EMPLOYMENT STABILITY & INCOME VALIDATION", [
            "Verification of repayment capacity is the cornerstone of the underwriting process.",
            "- Tenure Mandate: Minimum of 24 months continuous employment within the same industry.",
            "- Income Verification: Must be validated via primary source documentation (e.g., pay stubs, W-2).",
            "- Self-Employed Profiles: Subject to Section 14.2 (2 years of verified federal tax filings required).",
            "- Gaps in History: Any employment cessation exceeding 90 calendar days requires a certified explanation."
        ]),
        ("SECTION 5: FRAUD DETECTION & IDENTITY VERIFICATION", [
            "The Fraud Service agent must provide a high-confidence match for all identity markers.",
            "- Zero Tolerance Flags: SSN Mismatch or Invalid Government ID status results in immediate DENIAL.",
            "- Velocity Controls: Multiple inquiries within a 72-hour window trigger a suspicious activity report.",
            "- Red Flag Indicators: Discrepancies in address history or employer physical location require deep-dive."
        ]),
        ("SECTION 6: DISPUTE RESOLUTION & ADVERSE ACTION", [
            "In the event of a DENIAL, an Adverse Action Notice must be generated in compliance with Regulation B.",
            "Applicants have the right to request a manual reconsideration of the decision within 30 business days,",
            "provided new material evidence of creditworthiness is submitted for senior review."
        ])
    ]

    for title, lines in content:
        if y < 150:
            c.showPage()
            page_num += 1
            draw_header(c, page_num)
            y = height - 100

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        y -= 20
        c.setFont("Helvetica", 10)
        for line in lines:
            # Simple text wrap check
            if len(line) > 90:
                # Naive split for demo purposes
                parts = [line[i:i+90] for i in range(0, len(line), 90)]
                for p in parts:
                    c.drawString(70, y, p)
                    y -= 15
            else:
                c.drawString(70, y, line)
                y -= 15
        y -= 15

    c.save()
    print(f"Balked-out Policy PDF created: {filename}")

if __name__ == "__main__":
    output_path = "external_services/confluence/Standard_Underwriting_Guidelines_2026.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    create_policy_pdf(output_path)
