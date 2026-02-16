from fpdf import FPDF
import random

def create_master_policy():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title Page
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 60, "", ln=True)
    pdf.cell(0, 20, "MASTER LENDING POLICY", align="C", ln=True)
    pdf.set_font("Arial", "", 16)
    pdf.cell(0, 10, "Version 2024.2", align="C", ln=True)
    pdf.cell(0, 10, "Confidential - Internal Use Only", align="C", ln=True)
    
    # Filler generator
    import pypdf
    import os
    import random
    
    # Load real text from downloaded PDFs
    real_text_pool = []
    pdf_dir = "loan_approval_agent/data/policy_docs"
    for filename in ["OCC_Comptrollers_Handbook_Retail_Lending.pdf", "Fair4All_Lending_Policy.pdf"]:
        path = os.path.join(pdf_dir, filename)
        if os.path.exists(path):
            try:
                reader = pypdf.PdfReader(path)
                for page in reader.pages[:20]: # First 20 pages of each
                    text = page.extract_text()
                    if text and len(text) > 100:
                        real_text_pool.append(text)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
    if not real_text_pool:
        real_text_pool = ["Standard corporate compliance text. " * 50]

    def add_filler_pages(num_pages, section_title):
        pdf.set_font("Arial", "", 11)
        
        for i in range(num_pages):
            pdf.add_page()
            # Header
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"{section_title} - Page {i+1}", ln=True)
            pdf.line(10, 20, 200, 20)
            pdf.ln(10)
            
            # Content (Real Text mix)
            pdf.set_font("Arial", "", 11)
            
            # Create a "Section"
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Section {random.randint(100, 999)}.{random.randint(1,99)} - {section_title} Detail", ln=True)
            pdf.set_font("Arial", "", 11)
            
            # Add 2-3 paragraphs of real text
            for _ in range(random.randint(2, 4)):
                text_chunk = random.choice(real_text_pool)
                # Clean up a bit
                text_chunk = text_chunk.replace('\n', ' ').strip()
                
                # Sanitize for FPDF (Latin-1 only)
                # Replace common offenders
                replacements = {
                    '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
                    '\u2013': '-', '\u2014': '-', '\u2022': '-', '\u00a0': ' '
                }
                for k, v in replacements.items():
                    text_chunk = text_chunk.replace(k, v)
                
                # Strip remaining non-latin-1
                text_chunk = text_chunk.encode('latin-1', 'ignore').decode('latin-1')

                # Take a random slice to avoid huge blocks if needed
                if len(text_chunk) > 1500:
                     start = random.randint(0, len(text_chunk)-1500)
                     text_chunk = text_chunk[start:start+1500]
                
                try:
                    pdf.multi_cell(0, 6, text_chunk[:2000]) # Safety cap
                except Exception as e:
                   print(f"Skipping chunk due to error: {e}")
                pdf.ln(5)

    # 1. Governance (Filler)
    add_filler_pages(10, "Governance & Compliance")

    # 2. Credit Policy (The Meat)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SECTION 4: CREDITWORTHINESS ASSESSMENT", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    
    policy_text = """
    4.1 Minimum Credit Score Requirements
    The Bank requires a minimum FICO score of 720 for automatic approval.
    Applicants with scores between 660 and 719 will be referred for Manual Review.
    Applicants with scores below 660 shall be declined, unless a specific exception applies (see Section 4.5).
    
    4.2 Debt-to-Income (DTI) Ratio
    Maximum acceptable DTI is 36% for auto-approval.
    DTI up to 43% is acceptable if the applicant has a FICO score > 750 ("The High Earner Exception").
    
    4.3 Bankruptcy & Delinquency
    Any bankruptcy in the last 7 years is an automatic decline.
    More than 1 late payment in the last 12 months requires Manual Review.
    """
    pdf.multi_cell(0, 10, policy_text)
    
    add_filler_pages(20, "Credit Reporting Standards")

    # 3. Income Policy
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SECTION 7: INCOME VERIFICATION", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    
    income_text = """
    7.1 Salaried Employees
    Must provide 2 most recent pay stubs and W2.
    Employment tenure must be > 2 years for standard approval.
    Tenure < 2 years requires Manual Review ("Young Professional Check").
    
    7.2 Self-Employed Applicants
    Must provide 2 years of tax returns.
    Income is calculated as the average of the last 2 years Net Income.
    Declining income trend over the last 2 years triggers automatic decline.
    """
    pdf.multi_cell(0, 10, income_text)
    
    add_filler_pages(30, "Tax Documentation Standards")

    # 4. Risk Policy
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SECTION 12: RISK & FRAUD PREVENTION", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    
    risk_text = """
    12.1 Fraud Signals
    Any Fraud Score > 80 is an automatic decline.
    Identity Verification failure is an automatic decline.
    
    12.2 Prohibited Industries
    Loans shall not be approved for businesses in the following sectors:
    - Adult Entertainment
    - Cannabis / Marijuana related businesses
    - Gambling / Casinos
    """
    pdf.multi_cell(0, 10, risk_text)
    
    add_filler_pages(50, "Regulatory Disclosures")

    # Save
    import os
    output_path = "loan_approval_agent/data/policy_docs/Master_Lending_Policy_v2024.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"Generated bulky policy at {output_path}")

if __name__ == "__main__":
    create_master_policy()
