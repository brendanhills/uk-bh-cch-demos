import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT_DIR = "data/drive_content"

def create_pdf(filename, title, content_lines):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    for line in content_lines:
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    print(f"Created PDF: {filepath}")

def create_md(filename, title, content):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(f"# {title}\n\n")
        f.write(content)
    print(f"Created MD: {filepath}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. THE TARGET: Client Gift Policy
    create_pdf(
        "Client_Gift_Policy_2024.pdf",
        "CEBank Client Gift & Entertainment Policy (2024)",
        [
            "Effective Date: January 1, 2024",
            "Owner: Compliance Department",
            "Sensitivity: Internal",
            "",
            "1. Purpose",
            "This policy establishes the standards for giving and receiving gifts and entertainment to ensure impartial business decision-making.",
            "",
            "2. General Limits",
            "Employees may not accept or provide gifts that are lavish or excessive. The following specific limits apply:",
            "- Gifts: The maximum value for a single gift is $50 USD. Gifts valued between $50 and $150 require Line Manager approval.",
            "- Entertainment: Ordinary business meals are permitted up to $150 USD per person. Anything above this requires Compliance pre-approval.",
            "",
            "3. Prohibited Items",
            "Cash or cash equivalents (gift cards) are strictly prohibited regardless of value.",
            "Gifts to government officials are prohibited without pre-clearance from Legal.",
            "",
            "4. Reporting",
            "All gifts and entertainment events valued at over $20 must be recorded in the Gift Registry portal within 5 business days.",
        ]
    )

    # 2. Remote Work Policy
    create_pdf(
        "Remote_Work_Gridelines.pdf",
        "Flexible & Remote Work Guidelines",
        [
            "Policy: HR-2023-09",
            "All employees are eligible for hybrid work (3 days in office, 2 days remote) after completing their probation period.",
            "Remote work days must be agreed upon with your line manager.",
            "Employees must ensure they have a secure internet connection and a private workspace.",
            "VPN usage is mandatory for accessing internal systems from home."
        ]
    )

    # 3. Social Media Policy
    create_pdf(
        "Social_Media_Policy.pdf",
        "Social Media Usage Policy",
        [
            "Employees must not post confidential information about CEBank or its clients on social media.",
            "Do not speak on behalf of the bank unless authorized by Public Relations.",
            "Be respectful in all online communications. Harassment or discrimination will not be tolerated."
        ]
    )

    # 4. IT: VPN Setup (MD)
    create_md(
        "IT_Guide_VPN_Setup.md",
        "How to setup CEBank VPN",
        """
1. **Download the Client**: Go to https://vpn.cebank.internal and download the GlobalProtect agent.
2. **Install**: Run the installer and restart your machine.
3. **Configure**: Enter the portal address: `vpn.cebank.com`.
4. **Login**: Use your standard AD credentials and approve the MFA push.
5. **Issues**: If you cannot connect, check your wifi connection or call the Helpdesk at x5555.
        """
    )

    # 5. IT: Printer Troubleshooting (MD)
    create_md(
        "IT_Guide_Printers.md",
        "Printer Troubleshooting Guide",
        """
- **Paper Jam**: Open tray 2 and check for obstructions.
- **Toner Low**: Contact Office Services. Do not shake the toner cartridge.
- **Secure Print**: Remember to tap your badge to release your print job.
- **Mapping**: To map a new printer, run `\\\\print-server\\` and double click the printer name.
        """
    )
    
    # 6. IT: Wifi Guest Access (PDF)
    create_pdf(
        "IT_Wifi_Guest_Access.pdf",
        "Guest Wifi Access Procedures",
        [
            "Network Name: CEBank-Guest",
            "Password: Changes weekly. Current password is provided at Reception.",
            "Restrictions: Guest wifi does not provide access to internal resources or printers.",
            "Duration: Guest accounts are valid for 24 hours."
        ]
    )

    # 7. HR: Holidays 2024 (PDF)
    create_pdf(
        "HR_Holiday_Calendar_2024.pdf",
        "2024 Bank Holiday Calendar (UK/US)",
        [
            "Jan 1: New Year's Day",
            "Jan 15: MLK Day (US Only)",
            "Mar 29: Good Friday",
            "May 27: Memorial Day (US) / Spring Bank Holiday (UK)",
            "Jul 04: Independence Day (US Only)",
            "Dec 25: Christmas Day",
            "Dec 26: Boxing Day (UK Only)"
        ]
    )

    # 8. HR: Expense Policy (PDF)
    create_pdf(
        "HR_Expense_Reimbursement_Policy.pdf",
        "Global Expense Reimbursement Policy",
        [
            "Receipts are required for all expenses over $25.",
            "Expenses must be submitted within 30 days of the transaction.",
            "Air Travel: Economy class for flights under 6 hours. Business class allowed for flights over 6 hours with VP approval.",
            "Hotels: Maximum rate of $300/night in major cities (NY, London, HK)."
        ]
    )

    # 9. HR: New Hire Checklist (MD)
    create_md(
        "HR_New_Hire_Onboarding.md",
        "Manager Checklist for New Hires",
        """
- [ ] Order Laptop and Phone (IT Service Portal)
- [ ] Assign Desk (Space Planning)
- [ ] Schedule Team Lunch
- [ ] Add to relevant email distribution lists
- [ ] Schedule intro meetings with key stakeholders
- [ ] Assign 'Buddy' for first week
        """
    )

    # 10. Project: Alpha Charter (PDF)
    create_pdf(
        "Project_Alpha_Charter.pdf",
        "Project Alpha - Platform Migration",
        [
            "Confidential - Internal Use Only",
            "Objective: Migrate legacy trading platform to Cloud.",
            "Budget: $5.2M",
            "Timeline: Q1 2024 - Q4 2025",
            "Sponsor: Edward Exec",
            "Risks: High complexity in data migration."
        ]
    )

    # 11. Project: Beta Minutes (MD)
    create_md(
        "Project_Beta_Minutes_2024_02_10.md",
        "Project Beta - Weekly Sync",
        """
**Date**: Feb 10, 2024
**Attendees**: Tim, Tina, Bob

**Updates**:
- UI design approved.
- Backend API facing latency issues.
- QA testing starts next week.

**Action Items**:
- Bob to investigate API latency.
- Tina to send new mocks to stakeholders.
        """
    )

    # 12. Template: Meeting Minutes (MD)
    create_md(
        "Template_Meeting_Minutes.md",
        "Meeting Minutes Template",
        """
**Date**: [Date]
**Attendees**: [List]

**Agenda**:
1. Topic A
2. Topic B

**Notes**:
- ...

**Action Items**:
- [Owner]: [Task]
        """
    )

    # 13. Event: Town Hall (PDF)
    create_pdf(
        "Comms_Q1_Town_Hall.pdf",
        "Q1 Global Town Hall Invitation",
        [
            "Join our CEO, Catherine, for the Q1 Town Hall.",
            "Date: March 15, 2024",
            "Time: 2:00 PM EST",
            "Topic: 2023 Results and 2024 Strategy.",
            "Submit questions in advance via Slido."
        ]
    )

    # 14. Strategy: 2025 Vision (Restricted) (PDF)
    create_pdf(
        "Strategy_2025_Vision_Confidential.pdf",
        "CEBank 2025 Strategic Vision (Strictly Confidential)",
        [
            "This document outlines the 3-year growth strategy.",
            "Key Focus Areas:",
            "1. Digital Transformation",
            "2. Expansion into APAC markets",
            "3. ESG Integration",
            "Target: 15% ROE by 2025."
        ]
    )
    
    # 15. Compliance: Whistleblower (PDF)
    create_pdf(
        "Compliance_Whistleblower_Policy.pdf",
        "Whistleblower Protection Policy",
        [
            "CEBank is committed to valid and ethical conduct.",
            "Employees are encouraged to report any suspected wrongdoing.",
            "Reports can be made anonymously via the Ethics Hotline.",
            "Retaliation against whistleblowers is strictly prohibited and grounds for termination."
        ]
    )

if __name__ == "__main__":
    main()
