
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_mock_payslip(filename="mock_payslip.pdf", name="Jane Doe", employer="Google DeepMind", period="Oct 2024", gross=6666.00, net=5000.00):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"PAYSLIP - {employer}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Employee: {name}")
    c.drawString(50, height - 100, f"Period: {period}")
    
    # Body
    c.line(50, height - 120, width - 50, height - 120)
    
    y = height - 150
    c.drawString(50, y, "Earnings")
    c.drawString(300, y, "Amount")
    y -= 20
    c.drawString(50, y, "Basic Salary")
    c.drawString(300, y, f"${gross:,.2f}")
    
    y -= 40
    c.drawString(50, y, "Deductions")
    y -= 20
    c.drawString(50, y, "Tax & Insurance")
    c.drawString(300, y, f"${(gross-net):,.2f}")
    
    c.line(50, y - 20, width - 50, y - 20)
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "NET PAY")
    c.drawString(300, y, f"${net:,.2f}")
    
    c.save()
    print(f"Created {filename}")

def create_mock_bank_statement(filename="mock_bank_statement.pdf", name="Jane Doe", balance=15000.00):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Global Bank - Statement of Account")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Account Holder: {name}")
    c.drawString(50, height - 100, f"Account Number: ****-1234")
    c.drawString(400, height - 80, "Date: Oct 31, 2024")
    
    # Summary
    c.line(50, height - 120, width - 50, height - 120)
    y = height - 150
    c.drawString(50, y, "Ending Balance")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, f"${balance:,.2f}")
    
    # Transactions
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recent Transactions")
    c.setFont("Helvetica", 10)
    y -= 25
    
    transactions = [
        ("Oct 01", "Opening Balance", "", "10,000.00"),
        ("Oct 15", "Salary Credit", "+5,000.00", "15,000.00"),
        ("Oct 20", "Rent Payment", "-2,000.00", "13,000.00"),
        ("Oct 25", "Groceries", "-300.00", "12,700.00"),
        ("Oct 30", "Consulting Income", "+2,300.00", "15,000.00")
    ]
    
    for date, desc, amt, bal in transactions:
        c.drawString(50, y, date)
        c.drawString(120, y, desc)
        c.drawString(300, y, amt)
        c.drawString(400, y, bal)
        y -= 20
        
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    os.makedirs("artifacts/uploads", exist_ok=True)
    create_mock_payslip("artifacts/uploads/mock_payslip.pdf", name="Jane Doe", gross=6666.00) # ~80k annual
    create_mock_bank_statement("artifacts/uploads/mock_bank_statement.pdf", name="Jane Doe")
