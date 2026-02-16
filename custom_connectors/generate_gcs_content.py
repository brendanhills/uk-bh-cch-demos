from fpdf import FPDF
import os
import datetime

# Configuration
OUTPUT_DIR = "gcs_content"
DOMAINS = ["brendanhills.altostrat.com"]

def ensure_dirs():
    for level in ["restricted", "internal", "public"]:
        path = os.path.join(OUTPUT_DIR, level)
        os.makedirs(path, exist_ok=True)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'CEBank International - Official Document', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(filename, title, content, sensitivity, authors=[]):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, 0, 1, 'L')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Sensitivity: {sensitivity} | Date: {datetime.date.today()}", 0, 1, 'L')
    pdf.cell(0, 10, f"Authors: {', '.join(authors)}", 0, 1, 'L')
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, content)
    
    pdf.output(filename)
    print(f"Generated PDF: {filename}")

def create_text(filename, title, content, sensitivity):
    with open(filename, "w") as f:
        f.write(f"TITLE: {title}\n")
        f.write(f"SENSITIVITY: {sensitivity}\n")
        f.write(f"DATE: {datetime.date.today()}\n")
        f.write("-" * 20 + "\n")
        f.write(content)
    print(f"Generated Text: {filename}")

def main():
    ensure_dirs()
    
    # 1. Restricted (Board Minutes) - Visible to Executives/Compliance
    create_pdf(
        f"{OUTPUT_DIR}/restricted/Board_Minutes_Q1_2024.pdf",
        "Q1 2024 Board Meeting Minutes - Confidential Strategy",
        "The board discussed the acquisition of FinTech invalid_name on 2024-03-15.\n"
        "Vote was unanimous. Access to this document is strictly limited to the Board and Compliance Officer.\n"
        "Key topics: Merger M&A, Executive Compensation, Strategic Pivot to AI.",
        "Restricted",
        ["Catherine CEO", "Edward Exec"]
    )
    
    # 2. Internal (Project Proposals) - Visible to Employees (Traders, etc.)
    create_pdf(
        f"{OUTPUT_DIR}/internal/Project_Titan_Proposal.pdf",
        "Project Titan - AI Trading Assistant",
        "Proposal to implement a new AI-driven assistant for the trading desk.\n"
        "Objective: Reduce manual trade entry time by 40%.\n"
        "Budget: $2.5M. Timeline: Q3 2024 - Q2 2025.\n"
        "Sponsor: Ian InvestmentBanker.",
        "Internal",
        ["Ian InvestmentBanker"]
    )

    # 3. Public (Press Releases) - Visible to Everyone
    create_text(
        f"{OUTPUT_DIR}/public/Press_Release_2024_01.txt",
        "CEBank Reports Record Earnings",
        "London, UK - CEBank International today announced record earnings for the fiscal year 2023.\n"
        "CEO Catherine commented: 'We are thrilled with the results and our commitment to sustainable finance.'\n"
        "The bank will be hosting a public webinar on Monday.",
        "Public"
    )

if __name__ == "__main__":
    main()
