#!/usr/bin/env python3
"""
AWS Document Generator
Generates high-fidelity synthetic AWS PDFs (Service Agreement, Invoice, FinOps Report).
"""

import os
import random
import calendar
from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, PageBreak
from scripts.pdf_utils import draw_address_block, draw_trend_indicator
from scripts.base_generator import StyleManager, BaseDocumentTemplate

AWS_COLOR = colors.HexColor("#FF9900")
PROVIDER_NAME = "AWS"

SUPPLIER_ADDR = [
    "Amazon Web Services Australia Pty Ltd",
    "Level 37, 2-26 Park St",
    "Sydney NSW 2000, Australia",
    "ABN: 63 605 382 190"
]

CSIRO_ADDR = [
    "CSIRO Black Mountain",
    "Clunies Ross St",
    "Black Mountain ACT 2601, Australia"
]

SERVICES = ["Amazon EC2", "Amazon S3", "AWS Lambda", "Amazon RDS", "Amazon DynamoDB"]

def generate_aws_service_agreement(file_path, date_str):
    """Generates a 5+ page high-fidelity AWS Service Agreement."""
    sm = StyleManager(PROVIDER_NAME, AWS_COLOR)
    story = []

    # Title Page
    story.append(Spacer(1, 2 * 72))
    story.append(Paragraph("AWS CUSTOMER AGREEMENT", sm.styles['TDA_Title']))
    story.append(Paragraph(f"Effective Date: {date_str}", sm.styles['Normal']))
    story.append(Paragraph(f"Agreement ID: AWS-AU-SA-{os.urandom(4).hex().upper()}", sm.styles['Normal']))
    story.append(Spacer(1, 1 * 72))
    
    story.append(Paragraph("This AWS Customer Agreement (this “Agreement”) contains the terms and conditions that govern your access to and use of the Service Offerings (as defined below) and is an agreement between Amazon Web Services Australia Pty Ltd (“AWS,” “we,” “us,” or “our”) and the Commonwealth Scientific and Industrial Research Organisation (“CSIRO,” “you,” or “your”).", sm.styles['LegalText']))
    
    story.append(PageBreak())

    # Sections to ensure 5+ pages
    sections = [
        ("1. USE OF THE SERVICE OFFERINGS", [
            "1.1 Generally. You may access and use the Service Offerings in accordance with this Agreement. Service Level Agreements and Service Terms apply to certain Service Offerings.",
            "1.2 Your Account. To access the Services, you must have an AWS account associated with a valid email address and a valid form of payment. Unless explicitly permitted by the Service Terms, you will only create one account per email address.",
            "1.3 Support. We will provide support for the Services to you in accordance with the AWS Support guidelines. For CSIRO, the Enterprise Support tier is active."
        ]),
        ("2. CHANGES", [
            "2.1 To the Service Offerings. We may change or discontinue any of the Service Offerings from time to time. We will provide at least 12 months' prior notice if we discontinue a material function of a Service Offering that you are using.",
            "2.2 To the APIs. We may change or discontinue any APIs for the Services from time to time. For any backward-incompatible change to a Service API, we will use commercially reasonable efforts to continue supporting the previous version of the API for 12 months after the change."
        ]),
        ("3. SECURITY AND DATA PRIVACY", [
            "3.1 AWS Security. Without limiting Section 10 or your obligations under Section 4.2, we will implement reasonable and appropriate measures designed to help you secure Your Content against accidental or unlawful loss, access or disclosure.",
            "3.2 Data Privacy. You may specify the AWS Regions in which Your Content will be stored. We will not move Your Content from the AWS Regions selected by you without notifying you, unless required to comply with the law.",
            "3.3 Australian Privacy Principles. AWS Australia complies with the Privacy Act 1988 (Cth) and the Australian Privacy Principles in handling personal information."
        ]),
        ("4. YOUR RESPONSIBILITIES", [
            "4.1 Your Accounts. Except to the extent caused by our breach of this Agreement, (a) you are responsible for all activities that occur under your account, regardless of whether authorized by you.",
            "4.2 Your Content. You will ensure that Your Content and your End Users’ use of Your Content or the Service Offerings will not violate any of the Policies or any applicable law.",
            "4.3 Your Security and Backup. You are responsible for properly configuring and using the Service Offerings and otherwise taking your own steps to maintain appropriate security."
        ]),
        ("5. FEES AND PAYMENT", [
            "5.1 Service Fees. We calculate and bill fees and charges monthly. You will pay us the applicable fees and charges for use of the Service Offerings as described on the AWS Site.",
            "5.2 Taxes. All fees and charges payable by you are exclusive of applicable taxes and duties, including GST. AWS Australia will issue tax invoices in accordance with Australian GST law."
        ]),
        ("6. TEMPORARY SUSPENSION", [
            "6.1 Generally. We may suspend your or any End User’s right to access or use any portion or all of the Service Offerings immediately upon notice to you if we determine a security risk exists."
        ]),
        ("7. TERM AND TERMINATION", [
            "7.1 Term. The term of this Agreement will commence on the Effective Date and will remain in effect until terminated under this Section 7.",
            "7.2 Termination for Convenience. You may terminate this Agreement for any reason by providing us notice and closing your account.",
            "7.3 Termination for Cause. Either party may terminate this Agreement for cause if the other party is in material breach and fails to cure within 30 days."
        ]),
        ("8. PROPRIETARY RIGHTS", [
            "8.1 Your Content. As between you and us, you or your licensors own all right, title, and interest in and to Your Content.",
            "8.2 Service Offerings License. We or our affiliates or licensors own all right, title, and interest in and to the Service Offerings."
        ]),
        ("9. INDEMNIFICATION", [
            "9.1 General. You will defend, indemnify, and hold harmless us, our affiliates and licensors, and each of their respective employees, officers, directors, and representatives from and against any claims, damages, losses, liabilities, costs, and expenses (including reasonable attorneys’ fees) arising out of or relating to any third party claim.",
            "9.2 Process. We will promptly notify you of any claim subject to Section 9.1, but our failure to promptly notify you will only affect your obligations under Section 9.1 to the extent that our failure prejudices your ability to defend the claim."
        ]),
        ("10. LIMITATIONS OF LIABILITY", [
            "10.1 Disclaimer of Indirect Damages. WE AND OUR AFFILIATES AND LICENSORS WILL NOT BE LIABLE TO YOU FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR EXEMPLARY DAMAGES (INCLUDING DAMAGES FOR LOSS OF PROFITS, REVENUES, CUSTOMERS, OPPORTUNITIES, GOODWILL, USE, OR DATA).",
            "10.2 Liability Cap. OUR AND OUR AFFILIATES’ AND LICENSORS’ AGGREGATE LIABILITY UNDER THIS AGREEMENT WILL NOT EXCEED THE AMOUNT YOU ACTUALLY PAID US UNDER THIS AGREEMENT FOR THE SERVICE THAT GAVE RISE TO THE CLAIM DURING THE 12 MONTHS BEFORE THE LIABILITY AROSE."
        ]),
        ("11. MISCELLANEOUS", [
            "11.1 Force Majeure. We and our affiliates will not be liable for any delay or failure to perform any obligation under this Agreement where the delay or failure results from any cause beyond our reasonable control.",
            "11.2 Independent Contractors. We and you are independent contractors, and this Agreement will not be construed to create a partnership, joint venture, agency, or employment relationship.",
            "11.3 Governing Law. The laws of New South Wales, Australia, without reference to conflict of law rules, govern this Agreement and any dispute of any sort that might arise between you and us.",
            "11.4 Entire Agreement. This Agreement incorporates the Policies by reference and is the entire agreement between you and us regarding the subject matter of this Agreement.",
            "11.5 Severability. If any portion of this Agreement is held to be invalid or unenforceable, the remaining portions of this Agreement will remain in full force and effect."
        ])
    ]

    for title, paras in sections:
        story.append(Paragraph(title, sm.styles['SectionHeader']))
        for p in paras:
            story.append(Paragraph(p, sm.styles['LegalText']))
            story.append(Spacer(1, 10))
        # Strategic page breaks to push past 5 pages
        if title in ["2. CHANGES", "4. YOUR RESPONSIBILITIES", "6. TEMPORARY SUSPENSION", "8. PROPRIETARY RIGHTS", "10. LIMITATIONS OF LIABILITY"]:
            story.append(PageBreak())

    doc = BaseDocumentTemplate(file_path, sm, "Service Agreement")
    doc.build_flowable(story)

def generate_aws_invoice(file_path, date_str):
    """Generates a high-fidelity synthetic AWS Invoice (Canvas based)."""
    sm = StyleManager(PROVIDER_NAME, AWS_COLOR)
    
    doc_date = date.fromisoformat(date_str)
    last_day = calendar.monthrange(doc_date.year, doc_date.month)[1]
    billing_start = doc_date.replace(day=1).strftime("%d %b %Y")
    billing_end = doc_date.replace(day=last_day).strftime("%d %b %Y")
    
    def draw_callback(c):
        width, height = LETTER
        
        # Metadata
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, "INVOICE DETAILS")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 180, f"Date: {date_str}")
        c.drawString(50, height - 195, f"Document ID: AWS-INV-{os.urandom(4).hex().upper()}")
        c.drawString(50, height - 210, f"Customer ID: CSIRO-AU-2026")
        c.drawString(50, height - 225, f"Currency: AUD")
        
        draw_address_block(c, "Service Provider:", SUPPLIER_ADDR, width - 50, height - 180, align='right')
        draw_address_block(c, "Customer Address:", CSIRO_ADDR, 50, height - 250)

        y = height - 340
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Billing Period: {billing_start} to {billing_end}")
        y -= 30
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Summary of Charges")
        c.line(50, y - 5, width - 50, y - 5)
        y -= 25
        
        data = [["Service Description", "Amount (AUD)"]]
        total = 0
        for svc in SERVICES:
            base_cost = 1000 + (doc_date.month * 50)
            cost = random.uniform(base_cost * 0.8, base_cost * 1.2)
            data.append([svc, f"${cost:,.2f}"])
            total += cost
        
        gst = total * 0.1
        grand_total = total + gst
        data.append(["Subtotal (ex-GST)", f"${total:,.2f}"])
        data.append(["GST (10%)", f"${gst:,.2f}"])
        data.append(["TOTAL DUE", f"${grand_total:,.2f}"])
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(AWS_COLOR)
        c.rect(50, y - 5, width - 100, 20, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.drawString(60, y, "Service Description")
        c.drawRightString(width - 60, y, "Amount (AUD)")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        y -= 25
        for row in data[1:]:
            c.drawString(60, y, row[0])
            c.drawRightString(width - 60, y, row[1])
            y -= 18

    doc = BaseDocumentTemplate(file_path, sm, "Invoice")
    doc.build_canvas(draw_callback)

def generate_aws_finops_report(file_path, date_str):
    """Generates a detailed high-fidelity AWS FinOps Report."""
    sm = StyleManager(PROVIDER_NAME, AWS_COLOR)
    doc_date = date.fromisoformat(date_str)
    
    def draw_callback(c):
        width, height = LETTER
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, "FINOPS PERFORMANCE SUMMARY")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 180, f"Reporting Month: {doc_date.strftime('%B %Y')}")
        c.drawString(50, height - 195, f"Account: CSIRO-AWS-CONSOLIDATED")
        
        draw_address_block(c, "Prepared For:", CSIRO_ADDR, width - 50, height - 180, align='right')

        y = height - 260
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Cloud Spend & Trend Analysis")
        c.line(50, y - 5, width - 50, y - 5)
        y -= 30
        
        y = draw_trend_indicator(c, 50, y, "Total Amortized Spend", f"AUD {random.uniform(15000, 25000):,.2f}", random.uniform(-10, 10))
        y = draw_trend_indicator(c, 250, y + 40, "Budget Variance", f"{random.uniform(-3, 3):.1f}%", random.uniform(-1, 1))
        y = draw_trend_indicator(c, 450, y + 40, "Commitment Coverage", f"{random.uniform(82, 94):.1f}%", random.uniform(-2, 2))
        
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Service-Level Detail")
        y -= 20
        
        header = ["Service", "Spend (MoM)", "Change %"]
        y_table = y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y_table, header[0])
        c.drawString(250, y_table, header[1])
        c.drawRightString(width - 60, y_table, header[2])
        c.line(50, y_table - 5, width - 50, y_table - 5)
        y_table -= 20
        
        c.setFont("Helvetica", 10)
        for svc in SERVICES:
            spend = random.uniform(2000, 5000)
            change = random.uniform(-8, 12)
            c.drawString(60, y_table, svc)
            c.drawString(250, y_table, f"AUD {spend:,.2f}")
            color = colors.red if change > 0 else colors.green
            c.setFillColor(color)
            c.drawRightString(width - 60, y_table, f"{'+' if change > 0 else ''}{change:.1f}%")
            c.setFillColor(colors.black)
            y_table -= 15
            
        y = y_table - 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Optimization Opportunities (AWS Trusted Advisor)")
        y -= 20
        c.setFont("Helvetica", 10)
        insights = [
            f"• EC2 Rightsizing: {random.randint(5, 12)} instances in AP-SOUTHEAST-2 are idle. Save AUD {random.uniform(400, 1200):.2f}/mo.",
            f"• S3 Storage: Identified {random.randint(10, 40)} TB of data eligible for S3 Glacier Instant Retrieval.",
            f"• Savings Plans: $0.45/hr of uncommitted spend detected in RDS. Purchase recommended."
        ]
        for insight in insights:
            c.drawString(50, y, insight)
            y -= 15

    doc = BaseDocumentTemplate(file_path, sm, "FinOps Report")
    doc.build_canvas(draw_callback)

if __name__ == "__main__":
    generate_aws_service_agreement("aws_sa_sample.pdf", "2026-05-05")
    generate_aws_invoice("aws_invoice_sample.pdf", "2026-05-05")
    generate_aws_finops_report("aws_report_sample.pdf", "2026-05-05")
