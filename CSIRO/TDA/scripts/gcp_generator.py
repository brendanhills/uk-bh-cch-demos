#!/usr/bin/env python3
"""
GCP Document Generator
Generates high-fidelity synthetic GCP PDFs (Service Agreement, Invoice, FinOps Report).
"""

import os
import random
import calendar
from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from scripts.pdf_utils import (
    draw_header, draw_footer, draw_address_block, draw_trend_indicator,
    draw_header_canvas, draw_footer_canvas, get_styles
)

GCP_COLOR = colors.HexColor("#34A853")
PROVIDER_NAME = "Google Cloud"

SUPPLIER_ADDR = [
    "Google Australia Pty Ltd",
    "48 Pirrama Rd",
    "Pyrmont NSW 2009, Australia",
    "ABN: 33 102 769 994"
]

CSIRO_ADDR = [
    "CSIRO Data61",
    "13 Garden St",
    "Eveleigh NSW 2015, Australia"
]

SERVICES = ["Compute Engine", "Cloud Storage", "Cloud Functions", "Cloud SQL", "BigQuery"]

def generate_gcp_service_agreement(file_path, date_str):
    """Generates a 5+ page high-fidelity GCP Service Agreement."""
    styles = get_styles()
    doc = SimpleDocTemplate(str(file_path), pagesize=LETTER)
    story = []

    story.append(Spacer(1, 2 * 72))
    story.append(Paragraph("GOOGLE CLOUD PLATFORM TERMS OF SERVICE", styles['TDA_Title']))
    story.append(Paragraph(f"Effective Date: {date_str}", styles['Normal']))
    story.append(Paragraph(f"Contract ID: GCP-AU-SA-{os.urandom(4).hex().upper()}", styles['Normal']))
    story.append(Spacer(1, 1 * 72))
    
    story.append(Paragraph("These Google Cloud Platform Terms of Service (the “Agreement”) are entered into by Google Australia Pty Ltd (“Google”) and the Commonwealth Scientific and Industrial Research Organisation (“CSIRO,” “Customer,” “you,” or “your”).", styles['LegalText']))
    
    story.append(PageBreak())

    sections = [
        ("1. PROVISION OF THE SERVICES", [
            "1.1 Services Use. During the Term, Google will provide the Services in accordance with the Agreement, including the SLAs.",
            "1.2 Admin Console. Google will provide Customer access to the Admin Console through which Customer may manage its use of the Services.",
            "1.3 Accounts. Customer must have an Account to use the Services and is responsible for the information it provides.",
            "1.4 Modifications. Google may make commercially reasonable updates to the Services from time to time."
        ]),
        ("2. DATA PROCESSING AND SECURITY", [
            "2.1 Data Processing Terms. The Data Processing Amendment (Cloud) is incorporated by reference.",
            "2.2 Data Residency. Customer may select where certain Customer Data will be stored at rest (the “Data Location Selection”).",
            "2.3 Australian Privacy Act. Google Australia maintains compliance with the Privacy Act 1988 (Cth) and handles personal information accordingly."
        ]),
        ("3. CUSTOMER OBLIGATIONS", [
            "3.1 Compliance. Customer will (a) ensure that Customer and its End Users’ use of the Services complies with the Agreement.",
            "3.2 Shared Responsibility. Customer is responsible for properly configuring the Services and taking its own steps to maintain security."
        ]),
        ("4. PAYMENT TERMS", [
            "4.1 Billing and Payment. All fees are in Australian Dollars (AUD). Google will bill Customer monthly for use of the Services.",
            "4.2 Taxes. Google Australia will issue valid Tax Invoices including GST (10%) in accordance with Australian law."
        ]),
        ("5. INTELLECTUAL PROPERTY RIGHTS", [
            "5.1 IP Ownership. Except as expressly set forth, the Agreement does not grant either party any rights to the other’s intellectual property.",
            "5.2 Customer Data. Google may only use Customer Data to provide the Services and as otherwise specified in the Data Processing Amendment."
        ]),
        ("6. TERM AND TERMINATION", [
            "6.1 Agreement Term. The Agreement will remain in effect until terminated in accordance with this Section 6.",
            "6.2 Termination for Breach. Either party may terminate the Agreement if the other party is in material breach.",
            "6.3 Termination for Convenience. Customer may stop using the Services at any time."
        ]),
        ("7. LIMITATION OF LIABILITY", [
            "7.1 Liability Limit. Google’s total aggregate liability for all claims is limited to the fees Customer paid during the 12 months before the event.",
            "7.2 Exclusion of Indirect Damages. Neither party will be liable for lost revenues or indirect, special, incidental, or consequential damages."
        ]),
        ("8. INDEMNIFICATION", [
            "8.1 Google Indemnification. Google will defend Customer and its Affiliates against Intellectual Property Proceedings.",
            "8.2 Customer Indemnification. Customer will defend Google and its Affiliates against Intellectual Property Proceedings arising from Customer Data."
        ]),
        ("9. CONFIDENTIALITY", [
            "9.1 Protection. The recipient will not disclose the Confidential Information, except to Affiliates, employees, agents, or professional advisors.",
            "9.2 Required Disclosure. The recipient may disclose Confidential Information when required by law after giving reasonable notice to the discloser."
        ]),
        ("10. MISCELLANEOUS", [
            "10.1 Notices. All notices must be in writing and addressed to the other party’s legal department or primary contact.",
            "10.2 Force Majeure. Neither party will be liable for failure or delay in performance to the extent caused by circumstances beyond its control.",
            "10.3 Governing Law. All claims arising out of or relating to this Agreement will be governed by the laws of New South Wales, Australia."
        ])
    ]

    for title, paras in sections:
        story.append(Paragraph(title, styles['SectionHeader']))
        for p in paras:
            story.append(Paragraph(p, styles['LegalText']))
            story.append(Spacer(1, 10))
        if title in ["2. DATA PROCESSING AND SECURITY", "4. PAYMENT TERMS", "6. TERM AND TERMINATION", "8. INDEMNIFICATION", "9. CONFIDENTIALITY"]:
            story.append(PageBreak())

    def on_page(canvas, doc):
        draw_header_canvas(canvas, doc, PROVIDER_NAME, GCP_COLOR, "Service Agreement")
        draw_footer_canvas(canvas, doc, PROVIDER_NAME)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

def generate_gcp_invoice(file_path, date_str):
    """Generates a high-fidelity synthetic GCP Invoice (Canvas based)."""
    c = canvas.Canvas(str(file_path), pagesize=LETTER)
    width, height = LETTER
    
    doc_date = date.fromisoformat(date_str)
    last_day = calendar.monthrange(doc_date.year, doc_date.month)[1]
    billing_start = doc_date.replace(day=1).strftime("%d %b %Y")
    billing_end = doc_date.replace(day=last_day).strftime("%d %b %Y")
    
    draw_header(c, PROVIDER_NAME, GCP_COLOR, "Invoice")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 160, "INVOICE INFORMATION")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 180, f"Date: {date_str}")
    c.drawString(50, height - 195, f"Invoice ID: GCP-INV-{os.urandom(4).hex().upper()}")
    c.drawString(50, height - 210, f"Billing Account: CSIRO-AU-INT")
    c.drawString(50, height - 225, f"Currency: AUD")
    
    draw_address_block(c, "Service Provider:", SUPPLIER_ADDR, width - 50, height - 180, align='right')
    draw_address_block(c, "Customer Address:", CSIRO_ADDR, 50, height - 250)

    y = height - 340
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Usage Period: {billing_start} to {billing_end}")
    y -= 30
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Summary of Charges")
    c.line(50, y - 5, width - 50, y - 5)
    y -= 25
    
    data = [["GCP Service", "Amount (AUD)"]]
    total = 0
    for svc in SERVICES:
        base_cost = 900 + (doc_date.month * 60)
        cost = random.uniform(base_cost * 0.8, base_cost * 1.2)
        data.append([svc, f"${cost:,.2f}"])
        total += cost
    
    gst = total * 0.1
    grand_total = total + gst
    data.append(["Subtotal (ex-GST)", f"${total:,.2f}"])
    data.append(["GST (10%)", f"${gst:,.2f}"])
    data.append(["TOTAL DUE", f"${grand_total:,.2f}"])
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(GCP_COLOR)
    c.rect(50, y - 5, width - 100, 20, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.drawString(60, y, "GCP Service")
    c.drawRightString(width - 60, y, "Amount (AUD)")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    y -= 25
    for row in data[1:]:
        c.drawString(60, y, row[0])
        c.drawRightString(width - 60, y, row[1])
        y -= 18

    draw_footer(c, PROVIDER_NAME)
    c.showPage()
    c.save()

def generate_gcp_finops_report(file_path, date_str):
    """Generates a detailed high-fidelity GCP FinOps Report."""
    c = canvas.Canvas(str(file_path), pagesize=LETTER)
    width, height = LETTER
    
    doc_date = date.fromisoformat(date_str)
    draw_header(c, PROVIDER_NAME, GCP_COLOR, "FinOps Report")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 160, "GOOGLE CLOUD BILLING ANALYSIS")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 180, f"Analysis Month: {doc_date.strftime('%B %Y')}")
    c.drawString(50, height - 195, f"Billing Account: CSIRO-AU-PRODUCTION")
    
    draw_address_block(c, "Prepared For:", CSIRO_ADDR, width - 50, height - 180, align='right')

    y = height - 260
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Cloud Spend & Operational Efficiency")
    c.line(50, y - 5, width - 50, y - 5)
    y -= 30
    
    y = draw_trend_indicator(c, 50, y, "Gross Cloud Spend", f"AUD {random.uniform(14000, 24000):,.2f}", random.uniform(-18, 18))
    y = draw_trend_indicator(c, 250, y + 40, "Unit Economics (Cost/Req)", f"AUD {random.uniform(0.02, 0.08):.4f}", random.uniform(-3, 3))
    y = draw_trend_indicator(c, 450, y + 40, "CUD Coverage", f"{random.uniform(60, 92):.1f}%", random.uniform(-6, 6))
    
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Project-Level Spend (BigQuery Analysis)")
    y -= 20
    
    header = ["Project ID", "Spend (MoM)", "Credits Used"]
    y_table = y
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, y_table, header[0])
    c.drawString(250, y_table, header[1])
    c.drawRightString(width - 60, y_table, header[2])
    c.line(50, y_table - 5, width - 50, y_table - 5)
    y_table -= 20
    
    projects = ["csiro-ai-research", "csiro-data-lake-prod", "csiro-network-ops", "csiro-security-auth", "csiro-sandbox-dev"]
    c.setFont("Helvetica", 10)
    for proj in projects:
        spend = random.uniform(2500, 5500)
        credits = random.uniform(50, 400)
        c.drawString(60, y_table, proj)
        c.drawString(250, y_table, f"AUD {spend:,.2f}")
        c.setFillColor(colors.green)
        c.drawRightString(width - 60, y_table, f"AUD -{credits:,.2f}")
        c.setFillColor(colors.black)
        y_table -= 15
        
    y = y_table - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Optimization & Recommender Insights")
    y -= 20
    c.setFont("Helvetica", 10)
    insights = [
        f"• Compute Engine: Identified {random.randint(15, 40)} VMs with 0% CPU for >7 days. Save AUD {random.uniform(300, 900):.2f}.",
        f"• BigQuery: Table {os.urandom(3).hex()} has high storage cost. Consider partitioning or expiration policies.",
        f"• Network: Inter-region egress for {random.choice(projects)} is up 25%. Investigate data gravity."
    ]
    for insight in insights:
        c.drawString(50, y, insight)
        y -= 15

    draw_footer(c, PROVIDER_NAME)
    c.showPage()
    c.save()

if __name__ == "__main__":
    generate_gcp_service_agreement("gcp_sa_sample.pdf", "2026-05-05")
    generate_gcp_invoice("gcp_invoice_sample.pdf", "2026-05-05")
    generate_gcp_finops_report("gcp_report_sample.pdf", "2026-05-05")
