#!/usr/bin/env python3
"""
Azure Document Generator
Generates high-fidelity synthetic Azure PDFs (Service Agreement, Invoice, FinOps Report).
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

AZURE_COLOR = colors.HexColor("#008AD7")
PROVIDER_NAME = "Azure"

SUPPLIER_ADDR = [
    "Microsoft Australia Pty Limited",
    "1 Denison St",
    "North Sydney NSW 2060, Australia",
    "ABN: 82 000 621 490"
]

CSIRO_ADDR = [
    "CSIRO Corporate Centre",
    "Building 101, Clunies Ross St",
    "Black Mountain ACT 2601, Australia"
]

SERVICES = ["Virtual Machines", "Blob Storage", "Azure Functions", "SQL Database", "Cosmos DB"]

def generate_azure_service_agreement(file_path, date_str):
    """Generates a 5+ page high-fidelity Azure Service Agreement."""
    sm = StyleManager(PROVIDER_NAME, AZURE_COLOR)
    story = []

    story.append(Spacer(1, 2 * 72))
    story.append(Paragraph("MICROSOFT AZURE CUSTOMER AGREEMENT", sm.styles['TDA_Title']))
    story.append(Paragraph(f"Effective Date: {date_str}", sm.styles['Normal']))
    story.append(Paragraph(f"Enrollment Number: AZ-AU-SA-{os.urandom(4).hex().upper()}", sm.styles['Normal']))
    story.append(Spacer(1, 1 * 72))
    
    story.append(Paragraph("This Microsoft Azure Customer Agreement (this “Agreement”) is between Microsoft Australia Pty Limited (“Microsoft,” “we,” “us,” or “our”) and the Commonwealth Scientific and Industrial Research Organisation (“CSIRO,” “Customer,” “you,” or “your”).", sm.styles['LegalText']))
    
    story.append(PageBreak())

    sections = [
        ("1. DEFINITIONS", [
            "“Affiliate” means any legal entity that a party owns, that owns a party, or that is under common ownership with a party.",
            "“Customer Data” means all data, including all text, sound, video, or image files, and software, that are provided to Microsoft by, or on behalf of, Customer.",
            "“SLA” means the Service Level Agreement commitments Microsoft makes regarding delivery and/or performance of an Online Service."
        ]),
        ("2. USAGE RIGHTS AND LIMITATIONS", [
            "2.1 License Grant. Microsoft grants Customer a non-exclusive, non-transferable, worldwide right to access and use the Online Services during the Term.",
            "2.2 Acceptable Use Policy. Customer may not use the Online Services in any way that is prohibited by the Acceptable Use Policy.",
            "2.3 Technical Account Manager. CSIRO is provided with a dedicated CSAM as part of the Unified Support agreement."
        ]),
        ("3. SECURITY, PRIVACY, AND DATA PROTECTION", [
            "3.1 Security Measures. Microsoft has implemented and will maintain appropriate technical and organizational measures to protect Customer Data.",
            "3.2 Data Residency. Microsoft will store and process Customer Data in Australia (Sydney and Melbourne regions).",
            "3.3 Compliance. Microsoft complies with the Privacy Act 1988 (Cth) and other applicable Australian data protection laws."
        ]),
        ("4. SUBSCRIPTIONS, ORDERING, AND PRICING", [
            "4.1 Ordering. Customer may order Online Services under this Agreement through a Microsoft portal.",
            "4.2 Pricing and Payment. Customer will pay all fees for the Online Services in accordance with the pricing terms.",
            "4.3 AUD Currency. All transactions and billing for CSIRO will be conducted in Australian Dollars (AUD)."
        ]),
        ("5. TERM, TERMINATION, AND SUSPENSION", [
            "5.1 Term. This Agreement is effective until the expiration or termination of the last Subscription.",
            "5.2 Termination for Cause. Either party may terminate this Agreement if the other party is in material breach.",
            "5.3 Suspension. Microsoft may suspend use of an Online Service to prevent unauthorized access to Customer Data."
        ]),
        ("6. WARRANTIES AND DISCLAIMERS", [
            "6.1 Limited Warranty. Microsoft warrants that the Online Services will perform in accordance with the applicable SLA.",
            "6.2 Disclaimer. Microsoft provides the Online Services “as is” and disclaims all other warranties."
        ]),
        ("7. LIMITATION OF LIABILITY", [
            "7.1 Limit. Each party’s maximum liability is limited to direct damages finally awarded in an amount not to exceed the amounts paid by Customer for the Online Service."
        ]),
        ("8. INDEMNIFICATION", [
            "8.1 Microsoft’s Obligations. Microsoft will defend Customer against any third-party claim that an Online Service infringes its patent, copyright, or trademark or makes intentional unlawful use of its trade secret.",
            "8.2 Customer’s Obligations. Customer will defend Microsoft against any third-party claim that Customer Content infringes its patent, copyright, or trademark."
        ]),
        ("9. CONFIDENTIALITY", [
            "9.1 Disclosure. Each party will take reasonable steps to protect the other’s Confidential Information and will use the other party’s Confidential Information only for purposes of the business relationship.",
            "9.2 Exclusions. Confidential Information does not include information that is or becomes publicly available without breach of this Agreement."
        ]),
        ("10. MISCELLANEOUS", [
            "10.1 Notices. Notices must be in writing and will be treated as delivered on the date received at the address.",
            "10.2 Assignment. Neither party may assign this Agreement without the other party's written consent.",
            "10.3 Governing Law. This Agreement is governed by the laws of New South Wales, Australia.",
            "10.4 Entire Agreement. This Agreement is the entire agreement between the parties regarding its subject matter.",
            "10.5 Force Majeure. Neither party will be liable for any failure in performance due to causes beyond that party’s reasonable control (such as fire, explosion, or power blackout)."
        ])
    ]

    for title, paras in sections:
        story.append(Paragraph(title, sm.styles['SectionHeader']))
        for p in paras:
            story.append(Paragraph(p, sm.styles['LegalText']))
            story.append(Spacer(1, 10))
        if title in ["1. DEFINITIONS", "3. SECURITY, PRIVACY, AND DATA PROTECTION", "5. TERM, TERMINATION, AND SUSPENSION", "7. LIMITATION OF LIABILITY", "9. CONFIDENTIALITY"]:
            story.append(PageBreak())

    doc = BaseDocumentTemplate(file_path, sm, "Service Agreement")
    doc.build_flowable(story)

def generate_azure_invoice(file_path, date_str):
    """Generates a high-fidelity synthetic Azure Invoice (Canvas based)."""
    sm = StyleManager(PROVIDER_NAME, AZURE_COLOR)
    
    doc_date = date.fromisoformat(date_str)
    last_day = calendar.monthrange(doc_date.year, doc_date.month)[1]
    billing_start = doc_date.replace(day=1).strftime("%d %b %Y")
    billing_end = doc_date.replace(day=last_day).strftime("%d %b %Y")
    
    def draw_callback(c):
        width, height = LETTER
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, "INVOICE SUMMARY")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 180, f"Date: {date_str}")
        c.drawString(50, height - 195, f"Invoice Number: AZ-INV-{os.urandom(4).hex().upper()}")
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
        
        data = [["Resource Type", "Amount (AUD)"]]
        total = 0
        for svc in SERVICES:
            base_cost = 1200 + (doc_date.month * 40)
            cost = random.uniform(base_cost * 0.8, base_cost * 1.2)
            data.append([svc, f"${cost:,.2f}"])
            total += cost
        
        gst = total * 0.1
        grand_total = total + gst
        data.append(["Subtotal (ex-GST)", f"${total:,.2f}"])
        data.append(["GST (10%)", f"${gst:,.2f}"])
        data.append(["TOTAL DUE", f"${grand_total:,.2f}"])
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(AZURE_COLOR)
        c.rect(50, y - 5, width - 100, 20, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.drawString(60, y, "Resource Type")
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

def generate_azure_finops_report(file_path, date_str):
    """Generates a detailed high-fidelity Azure FinOps Report."""
    sm = StyleManager(PROVIDER_NAME, AZURE_COLOR)
    doc_date = date.fromisoformat(date_str)
    
    def draw_callback(c):
        width, height = LETTER
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, "AZURE COST MANAGEMENT SUMMARY")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 180, f"Period: {doc_date.strftime('%B %Y')}")
        c.drawString(50, height - 195, f"Subscription: CSIRO-AZURE-ENTERPRISE")
        
        draw_address_block(c, "Prepared For:", CSIRO_ADDR, width - 50, height - 180, align='right')

        y = height - 260
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Financial Governance & Efficiency")
        c.line(50, y - 5, width - 50, y - 5)
        y -= 30
        
        y = draw_trend_indicator(c, 50, y, "Monthly Recurring Cost", f"AUD {random.uniform(16000, 26000):,.2f}", random.uniform(-12, 12))
        y = draw_trend_indicator(c, 250, y + 40, "Forecast Accuracy", f"{random.uniform(94, 99):.1f}%", random.uniform(-1, 1))
        y = draw_trend_indicator(c, 450, y + 40, "Reservation Coverage", f"{random.uniform(68, 90):.1f}%", random.uniform(-4, 4))
        
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Resource Utilization (Azure Advisor)")
        y -= 20
        
        header = ["Resource Group", "Spend (MoM)", "Savings Potential"]
        y_table = y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y_table, header[0])
        c.drawString(250, y_table, header[1])
        c.drawRightString(width - 60, y_table, header[2])
        c.line(50, y_table - 5, width - 50, y_table - 5)
        y_table -= 20
        
        rgs = ["Data61-Core", "Atmospheric-Research", "Energy-Systems", "Shared-Services", "CSIRO-Internal"]
        c.setFont("Helvetica", 10)
        for rg in rgs:
            spend = random.uniform(3000, 6000)
            potential = random.uniform(100, 800)
            c.drawString(60, y_table, rg)
            c.drawString(250, y_table, f"AUD {spend:,.2f}")
            c.setFillColor(colors.green)
            c.drawRightString(width - 60, y_table, f"AUD {potential:,.2f}")
            c.setFillColor(colors.black)
            y_table -= 15
            
        y = y_table - 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Advisor Recommendations")
        y -= 20
        c.setFont("Helvetica", 10)
        insights = [
            f"• SQL Database: {random.randint(2, 5)} instances are over-provisioned. Save 15%.",
            f"• Cosmos DB: Autoscale throughput detected as inefficient for {random.randint(10, 30)}% of collections.",
            f"• Storage: Identified {random.uniform(1, 5):.1f} TB of orphaned managed disks."
        ]
        for insight in insights:
            c.drawString(50, y, insight)
            y -= 15

    doc = BaseDocumentTemplate(file_path, sm, "FinOps Report")
    doc.build_canvas(draw_callback)

if __name__ == "__main__":
    generate_azure_service_agreement("azure_sa_sample.pdf", "2026-05-05")
    generate_azure_invoice("azure_invoice_sample.pdf", "2026-05-05")
    generate_azure_finops_report("azure_report_sample.pdf", "2026-05-05")
