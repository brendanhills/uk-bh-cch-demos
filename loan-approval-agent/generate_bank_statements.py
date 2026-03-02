from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import random
from datetime import datetime, timedelta

def create_bank_statement(filename, name, account_number, balance, initial_date, num_transactions=60):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    def draw_header(canvas_obj, page_num):
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawCentredString(width/2, height - 50, "Global Trust Bank - Account Statement")
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawCentredString(width/2, height - 65, f"Account Holder: {name} | Account: {account_number}")
        canvas_obj.setFont("Helvetica-Oblique", 8)
        canvas_obj.drawCentredString(width/2, height - 80, f"Page {page_num}")
        canvas_obj.line(50, height - 85, width - 50, height - 85)

    page_num = 1
    draw_header(c, page_num)
    
    y = height - 120
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Statement Period: Jan 2026 - March 2026")
    y -= 20
    c.drawString(50, y, f"Opening Balance: USD {balance:,.2f}")
    y -= 30

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Transaction History")
    y -= 20
    
    c.setFont("Helvetica", 9)
    headers = ["Date", "Description", "Amount (USD)", "Type"]
    cols = [50, 150, 350, 450]
    for i, h in enumerate(headers):
        c.drawString(cols[i], y, h)
    y -= 15
    c.line(50, y+10, width-50, y+10)

    current_date = initial_date
    current_balance = balance
    
    descriptions = [
        "Grocery Mart", "Starbucks Coffee", "Amazon.com", "Shell Gas Station",
        "Utility Bill - Electric", "Water Dept", "City Hospital Payroll",
        "Rent Payment", "Gym Membership", "Internet Service", "Netflix Subscription",
        "Pharmacy Rx", "Hardware Store", "Fast Food Burger", "Local Diner",
        "Savings Transfer", "ATM Withdrawal", "Mobile Phone Bill", "Zelle Transfer",
        "Venmo Cash Out", "Unknown External Credit", "Check Deposit", "Wire Transfer In"
    ]

    for i in range(num_transactions):
        if y < 70:
            c.showPage()
            page_num += 1
            draw_header(c, page_num)
            y = height - 120
            c.setFont("Helvetica-Bold", 9)
            for j, h in enumerate(headers):
                c.drawString(cols[j], y, h)
            y -= 15
            c.line(50, y+10, width-50, y+10)
            c.setFont("Helvetica", 9)

        date_str = current_date.strftime("%Y-%m-%d")
        desc = random.choice(descriptions)
        
        # Scenario logic for fraud
        if name == "Jane Fraud" and i in [5, 15, 25]:
            desc = "Suspicious Offshore Wire"
            amt = 15000.00
            ttype = "CREDIT"
        elif "Payroll" in desc or "Deposit" in desc or "Credit" in desc or "Transfer In" in desc:
            amt = random.uniform(1000, 5000)
            ttype = "CREDIT"
        else:
            amt = -random.uniform(5, 800)
            ttype = "DEBIT"
            
        current_balance += amt
        
        c.drawString(cols[0], y, date_str)
        c.drawString(cols[1], y, desc)
        c.drawString(cols[2], y, f"{amt:,.2f}")
        c.drawString(cols[3], y, ttype)
        
        y -= 15
        current_date -= timedelta(days=random.randint(0, 2))

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Closing Balance: USD {current_balance:,.2f}")

    c.save()
    print(f"Balked-out Bank Statement created: {filename} ({num_transactions} txs)")

if __name__ == "__main__":
    output_dir = "artifacts/uploads"
    os.makedirs(output_dir, exist_ok=True)
    
    start_date = datetime(2026, 3, 1)
    
    personas = [
        ("Sarah Speed", "ACT-12345", 12000.00, 45),
        ("Gary Escalate", "ACT-34567", 1500.00, 45),
        ("Maria Agility", "ACT-90123", 45000.00, 60), # Healthy business account
        ("Jane Fraud", "ACT-99999", 50.00, 85) # Jane gets a massive statement
    ]
    
    for name, acc, bal, count in personas:
        filename = os.path.join(output_dir, f"bank_statement_{name.lower().replace(' ', '_')}.pdf")
        create_bank_statement(filename, name, acc, bal, start_date, count)
