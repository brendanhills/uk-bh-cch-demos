import json
import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load env for API key
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPLICANTS_FILE = os.path.join(BASE_DIR, "loan_approval_agent/data/demo_data/applicants.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "artifacts/uploads")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL_ID = os.environ.get("MODEL_FLASH", "gemini-2.5-flash")

def generate_pay_stub_data(applicant):
    """Uses Gemini to generate realistic pay stub data for an applicant."""
    
    prompt = f"""
    Generate realistic pay stub details for the following employee:
    Name: {applicant.get('name')}
    Employer: {applicant.get('employer')}
    Annual Income: ${applicant.get('stated_income')}
    Role: {applicant.get('role')}
    Tenure: {applicant.get('tenure')}

    The output must use this JSON schema:
    {{
        "employer_address": "string (realistic UK business address matching employer name)",
        "pay_period": "string (e.g. '01/01/2025 - 01/31/2025')",
        "pay_date": "string (e.g. '01/31/2025')",
        "hourly_rate": float (calculate based on income/2080, rounded to 2 decimals),
        "hours_worked": float (approx 160 for monthly),
        "gross_pay": float (income/12, rounded to 2 decimals),
        "deductions": {{
            "Federal Tax": float (approx 12% of gross),
            "State Tax": float (approx 4% of gross),
            "Social Security": float (6.2% of gross),
            "Medicare": float (1.45% of gross),
            "Health Insurance": float (random realistic amount),
            "401k": float (random realistic bit)
        }}
    }}
    
    Ensure the math is roughly correct but vary the deduction amounts slightly for realism.
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "employer_address": {"type": "STRING"},
                        "pay_period": {"type": "STRING"},
                        "pay_date": {"type": "STRING"},
                        "hourly_rate": {"type": "NUMBER"},
                        "hours_worked": {"type": "NUMBER"},
                        "gross_pay": {"type": "NUMBER"},
                        "deductions": {
                            "type": "OBJECT",
                            "properties": {
                                "Federal Tax": {"type": "NUMBER"},
                                "State Tax": {"type": "NUMBER"},
                                "Social Security": {"type": "NUMBER"},
                                "Medicare": {"type": "NUMBER"},
                                "Health Insurance": {"type": "NUMBER"},
                                "401k": {"type": "NUMBER"}
                            },
                            "required": ["Federal Tax", "State Tax", "Social Security", "Medicare"]
                        }
                    },
                    "required": ["employer_address", "pay_period", "pay_date", "hourly_rate", "hours_worked", "gross_pay", "deductions"]
                }
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating data with Gemini for {applicant.get('name')}: {e}")
        # Fallback to simple calculation if Gemini fails
        gross = applicant.get("stated_income", 0) / 12
        return {
            "employer_address": "123 Business Rd, UK",
            "pay_period": "01/01/2025 - 01/31/2025",
            "pay_date": "01/31/2025",
            "hourly_rate": applicant.get("stated_income", 0) / 2080,
            "hours_worked": 160.0,
            "gross_pay": gross,
            "deductions": {
                "Federal Tax": gross * 0.12,
                "State Tax": gross * 0.04,
                "Social Security": gross * 0.062,
                "Medicare": gross * 0.0145
            }
        }

def generate_pay_stub_pdf(applicant, data):
    name = applicant.get("name")
    employer = applicant.get("employer")
    
    # improved filename handling
    safe_name = name.lower().replace(" ", "_")
    pdf_path = os.path.join(OUTPUT_DIR, f"pay_stub_{safe_name}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "PAY REMITTANCE ADVICE")
    
    # Employer Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "Employer:")
    c.setFont("Helvetica", 12)
    c.drawString(150, height - 80, f"{employer}")
    
    # Handle long address by wrapping
    address = data["employer_address"]
    if len(address) > 40:
        # Simple split by comma or length
        parts = address.split(",")
        line1 = parts[0].strip()
        if len(parts) > 1:
             line1 += ","
        line2 = ", ".join(p.strip() for p in parts[1:])
        
        c.drawString(150, height - 95, line1)
        c.setFont("Helvetica", 10) # Smaller font for remaining lines
        c.drawString(150, height - 110, line2)
    else:
        c.drawString(150, height - 95, address)
    
    # Employee Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 130, "Employee:")
    c.setFont("Helvetica", 12)
    c.drawString(150, height - 130, name)
    c.drawString(150, height - 145, f"ID: EMP-{str(applicant.get('applicant_id', '000'))[-6:]}")
    
    # Period
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, height - 80, "Pay Period:")
    c.setFont("Helvetica", 12)
    c.drawString(400, height - 95, data["pay_period"])
    c.drawString(400, height - 110, f"Pay Date: {data['pay_date']}")
    
    # Line
    c.line(50, height - 160, width - 50, height - 160)
    
    # Earnings
    y = height - 190
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "EARNINGS")
    c.drawString(250, y, "RATE")
    c.drawString(350, y, "HOURS")
    c.drawString(450, y, "THIS PERIOD")
    
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Regular Pay")
    c.drawString(250, y, f"${data['hourly_rate']:,.2f}")
    c.drawString(350, y, f"{data['hours_worked']:,.2f}")
    c.drawString(450, y, f"${data['gross_pay']:,.2f}")
    
    # Total Gross
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "GROSS PAY")
    c.drawString(450, y, f"${data['gross_pay']:,.2f}")
    
    # Deductions
    y -= 40
    c.drawString(50, y, "DEDUCTIONS")
    y -= 20
    c.setFont("Helvetica", 12)
    
    total_deductions = 0
    for label, amount in data["deductions"].items():
        if amount > 0:
            c.drawString(50, y, label)
            c.drawString(450, y, f"-${amount:,.2f}")
            total_deductions += amount
            y -= 15
        
    # Net Pay
    net_pay = data["gross_pay"] - total_deductions
    y -= 25 # Extra spacing
    c.line(50, y+25, width - 50, y+25)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "NET PAY")
    c.drawString(450, y, f"${net_pay:,.2f}")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "This is a computer generated document. No signature required.")
    
    c.save()
    print(f"Created {pdf_path}")

def main():
    if not os.path.exists(APPLICANTS_FILE):
        print(f"Error: {APPLICANTS_FILE} not found.")
        return

    with open(APPLICANTS_FILE, "r") as f:
        applicants = json.load(f)

    for app in applicants:
        if app.get("employment_status") == "Employed":
            print(f"Generating pay stub for {app.get('name')}...")
            data = generate_pay_stub_data(app)
            generate_pay_stub_pdf(app, data)

if __name__ == "__main__":
    main()
