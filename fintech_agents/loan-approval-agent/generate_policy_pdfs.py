
import os
from fpdf import FPDF

# Mock policy content split by topic
POLICIES = {
    "credit_policy.pdf": """
# Credit Policy v2.0

## 1. Automated Approval Criteria
- **Credit Score**: Minimum 720 FICO.
- **Debt-to-Income (DTI)**: Maximum 36%.
- **Credit History**: No bankruptcies in the last 7 years. Minimum 3 years of credit history.

## 2. Manual Review Triggers
- Credit Score between 660 and 719.
- DTI between 36% and 43%.
- "Thin file" (less than 3 years history) but high income (> $100k).

## 3. Hard Decline Rules
- Credit Score < 660.
- active bankruptcy proceedings.
- Current delinquency on any mortgage or auto loan.
""",
    "employment_policy.pdf": """
# Employment Verification Policy v1.5

## 1. Income Stability
- Applicant must be at current employer for > 2 years OR have consistent employment history in the same industry for > 3 years.
- Self-employed applicants must provide 2 years of tax returns (simulated).

## 2. Acceptable Income Sources
- Salary / Wages (W-2)
- Self-employment income (1099) - requires 2-year average.
- Rental income (75% of lease value).
- Alimony/Child Support (must continue for > 3 years).

## 3. Unacceptable Income
- Assessing income from illegal activities.
- Projected future income without signed contract.
""",
    "risk_policy.pdf": """
# Risk & Compliance Policy v3.0

## 1. Fraud Detection
- **Identity mismatch**: SSN does not match name in credit bureau. -> DECLINE
- **Geo-velocity**: Multiple applications from different states in < 24 hours. -> FLAG FOR REVIEW

## 2. State Specific Exemptions
- **California**: DTI up to 45% allowed for W-2 employees with FICO > 740.
- **New York**: Medical debt collection accounts < $500 must be ignored.
- **Texas**: Cash-out refinance LTV limited to 80%.

## 3. Data Retention
- All declined applications must be retained for 7 years (FCRA).
"""
}

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Confidentail Internal Policy', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdfs():
    output_dir = "loan_approval_agent/data/policy_docs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean up old markdown files if they exist to avoid confusion
    for f in os.listdir(output_dir):
        if f.endswith(".md"):
            os.remove(os.path.join(output_dir, f))

    for filename, content in POLICIES.items():
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Simple markdown-ish to PDF conversion
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue
            
            if line.startswith('# '):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, line[2:], 0, 1)
                pdf.set_font("Arial", size=12)
            elif line.startswith('## '):
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, line[3:], 0, 1)
                pdf.set_font("Arial", size=12)
            elif line.startswith('- '):
                pdf.cell(10) # Indent
                pdf.multi_cell(0, 10, '- ' + line[2:])
            else:
                pdf.multi_cell(0, 10, line)
        
        output_path = os.path.join(output_dir, filename)
        pdf.output(output_path)
        print(f"Created {output_path}")

if __name__ == "__main__":
    create_pdfs()
