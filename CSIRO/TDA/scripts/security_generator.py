#!/usr/bin/env python3
"""
CSIRO Security & Privacy Standards Generator
Generates high-fidelity synthetic Security Standards PDF for the Security Agent.
Incorporates principles from the CSIRO Privacy Policy.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from scripts.pdf_utils import draw_header_canvas, draw_footer_canvas, get_styles

SECURITY_COLOR = colors.HexColor("#A50034") # CSIRO Maroon-ish
PROVIDER_NAME = "CSIRO Governance"

def generate_security_standards(file_path):
    """Generates a 5+ page high-fidelity CSIRO Security & Privacy Standards document."""
    styles = get_styles()
    doc = SimpleDocTemplate(str(file_path), pagesize=LETTER)
    story = []

    # Title Page
    story.append(Spacer(1, 2 * 72))
    story.append(Paragraph("MULTI-CLOUD SECURITY & PRIVACY STANDARDS", styles['TDA_Title']))
    story.append(Paragraph("Version: 2026.2", styles['Normal']))
    story.append(Paragraph("Classification: OFFICIAL: SENSITIVE", styles['Normal']))
    story.append(Spacer(1, 1 * 72))
    
    story.append(Paragraph("This document outlines the mandatory security, privacy, and governance standards for all cloud-based research and operational workloads within the Commonwealth Scientific and Industrial Research Organisation (CSIRO). It ensures alignment with the Privacy Act 1988 (Cth), the Australian Privacy Principles (APPs), and the Science and Industry Research Act 1949 (Cth).", styles['LegalText']))
    
    story.append(PageBreak())

    sections = [
        ("1. DATA COLLECTION AND PURPOSE", [
            "1.1 Purpose-Led Collection. Personal information must only be collected if it is necessary for, or directly related to, CSIRO’s functions or activities under the Science and Industry Research Act 1949 (Cth).",
            "1.2 Direct Collection. Where reasonably practicable, personal information should be collected directly from the individual to ensure accuracy and consent.",
            "1.3 Transparency and Notification. Specific 'Collection Notices' (APP 5) must be provided at the point of data entry detailing the purpose of collection, intended use, and any potential third-party disclosures.",
            "1.4 Sensitive Information. Higher scrutiny applies to health, genetic, or biometric data. Collection must be essential to the research and undergo a Privacy Impact Assessment (PIA)."
        ]),
        ("2. DATA USE, DISCLOSURE, AND DE-IDENTIFICATION", [
            "2.1 Primary Purpose Alignment. Information must only be used for the primary purpose for which it was collected. Secondary use requires explicit consent or legal mandate.",
            "2.2 Research De-identification. In research contexts, personal information should be de-identified as a default practice unless identifiable data is scientifically essential.",
            "2.3 Anonymized Analytics. Metadata collected via cloud services (e.g., IP addresses) must be used solely for improving service performance or specific research impact measurements.",
            "2.4 Third-Party Governance. Cloud service providers (e.g., AWS, Azure, GCP) must be contractually bound to laws or binding schemes substantially similar to the Australian Privacy Principles."
        ]),
        ("3. OVERSEAS DATA FLOWS", [
            "3.1 Overseas Disclosure (APP 8). Personal information may only be disclosed to overseas recipients if they are subject to similar privacy protections or explicit consent is obtained.",
            "3.2 Contractual Safeguards. All multi-cloud arrangements must include appropriate contractual measures to ensure privacy compliance by overseas recipients.",
            "3.3 Joint Venture Sharing. Data sharing with international partners must be limited to the specific business and administration purposes defined in official agreements."
        ]),
        ("4. SECURITY FRAMEWORK ALIGNMENT", [
            "4.1 Mandatory Frameworks. All cloud systems must comply with the Protective Security Policy Framework (PSPF) and the Australian Government Information Security Manual (ISM).",
            "4.2 Record-Keeping Obligations. Cloud data storage must adhere to the Archives Act 1983 (Cth) for proper preservation and disposal.",
            "4.3 Outsourced ICT Guidelines. Cloud arrangements must follow Australian Government Policy and Risk Management Guidelines for offshore environments.",
            "4.4 Access Control. Strict Role-Based Access Control (RBAC) and Multi-Factor Authentication (MFA) are mandatory for all systems handling CSIRO data."
        ]),
        ("5. DATA RESIDENCY AND SOVEREIGNTY", [
            "5.1 Mandatory Australian Hosting. Primary data stores containing 'Sensitive' or 'Protected' research data MUST reside within Australian geographic boundaries.",
            "5.2 Authorized Regions. Pre-approved regions include AWS Sydney/Melbourne, Azure Australia East/Southeast, and GCP Australia-Southeast1/2.",
            "5.3 Sovereignty Checks. Quarterly audits will verify that no unauthorized cross-border transfers of protected data have occurred."
        ]),
        ("6. AGENT GATEWAY AND GOVERNANCE", [
            "6.1 Mandatory Sign-off. Architectural recommendations from specialized Cloud Agents require a 'Pass' status from the Security Agent prior to implementation.",
            "6.2 Audit Logging. Every inter-agent consultation regarding security or privacy policy must be recorded in an immutable audit trail.",
            "6.3 Privacy Impact Assessments (PIA). New multi-cloud projects involving significant personal information handling must be registered in the CSIRO PIA Register."
        ]),
        ("7. ACCOUNTABILITY AND COMPLIANCE", [
            "7.1 Privacy Officer Oversight. A designated Privacy Officer (Governance) oversees compliance, manages the PIA Register, and handles investigations.",
            "7.2 Breach Notification. In the event of a data breach, CSIRO will follow the Notifiable Data Breaches (NDB) scheme as per the Privacy Act.",
            "7.3 Continuous Monitoring. Security and privacy controls are subject to continuous automated monitoring and manual quarterly reviews."
        ])
    ]

    for title, paras in sections:
        story.append(Paragraph(title, styles['SectionHeader']))
        for p in paras:
            story.append(Paragraph(p, styles['LegalText']))
            story.append(Spacer(1, 10))
        # Ensure 5+ pages by adding page breaks at logical points
        if title in ["2. DATA USE, DISCLOSURE, AND DE-IDENTIFICATION", "4. SECURITY FRAMEWORK ALIGNMENT", "6. AGENT GATEWAY AND GOVERNANCE"]:
            story.append(PageBreak())

    def on_page(canvas, doc):
        draw_header_canvas(canvas, doc, PROVIDER_NAME, SECURITY_COLOR, "Security & Privacy Standards")
        draw_footer_canvas(canvas, doc, PROVIDER_NAME)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

if __name__ == "__main__":
    generate_security_standards("csiro_security_standards.pdf")
