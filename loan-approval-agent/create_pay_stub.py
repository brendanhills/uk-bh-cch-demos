from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Output path
pdf_path = "/usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/artifacts/uploads/pay_stub.pdf"

# Ensure directory exists
os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

# Header
c.setFont("Helvetica-Bold", 16)
c.drawString(50, height - 50, "PAY REMITTANCE ADVICE")

# Employer Info
c.setFont("Helvetica-Bold", 12)
c.drawString(50, height - 80, "Employer:")
c.setFont("Helvetica", 12)
c.drawString(150, height - 80, "Medianville Manufacturing, Inc.")
c.drawString(150, height - 95, "123 Industria Way, Medianville, UK")

# Employee Info
c.setFont("Helvetica-Bold", 12)
c.drawString(50, height - 130, "Employee:")
c.setFont("Helvetica", 12)
c.drawString(150, height - 130, "Gary Gray")
c.drawString(150, height - 145, "ID: EMP-998877")

# Period
c.setFont("Helvetica-Bold", 12)
c.drawString(400, height - 80, "Pay Period:")
c.setFont("Helvetica", 12)
c.drawString(400, height - 95, "01/01/2025 - 01/15/2025")
c.drawString(400, height - 110, "Pay Date: 01/15/2025")

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
c.drawString(250, y, "$50.00")
c.drawString(350, y, "80.00")
c.drawString(450, y, "$4,000.00")

y -= 20
c.drawString(50, y, "Overtime")
c.drawString(250, y, "$75.00")
c.drawString(350, y, "0.00")
c.drawString(450, y, "$0.00")

# Total Gross
y -= 30
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "GROSS PAY")
c.drawString(450, y, "$4,000.00")

# Deductions
y -= 40
c.drawString(50, y, "DEDUCTIONS")
y -= 20
c.setFont("Helvetica", 12)
c.drawString(50, y, "Federal Tax")
c.drawString(450, y, "-$600.00")
y -= 15
c.drawString(50, y, "State Tax")
c.drawString(450, y, "-$150.00")
y -= 15
c.drawString(50, y, "Social Security")
c.drawString(450, y, "-$200.00")
y -= 15
c.drawString(50, y, "Medicare")
c.drawString(450, y, "-$50.00")

# Net Pay
y -= 40
c.line(50, y+25, width - 50, y+25)
c.setFont("Helvetica-Bold", 14)
c.drawString(50, y, "NET PAY")
c.drawString(450, y, "$3,000.00")

# Footer
c.setFont("Helvetica-Oblique", 10)
c.drawString(50, 50, "This is a computer generated document. No signature required.")

c.save()
print(f"Created {pdf_path}")
