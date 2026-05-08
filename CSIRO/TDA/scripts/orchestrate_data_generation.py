#!/usr/bin/env python3
"""
Orchestration Script for Synthetic Data Generation
Generates a 3-year history of localized cloud documents for CSIRO.
"""

import os
from pathlib import Path
from datetime import date
from scripts.aws_generator import generate_aws_service_agreement, generate_aws_invoice, generate_aws_finops_report
from scripts.azure_generator import generate_azure_service_agreement, generate_azure_invoice, generate_azure_finops_report
from scripts.gcp_generator import generate_gcp_service_agreement, generate_gcp_invoice, generate_gcp_finops_report
from scripts.finops_generator import generate_finops_csv
from scripts.security_generator import generate_security_standards

OUTPUT_DIR = Path("synthetic_data/cloud_finops")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate Annual Security Standards
    generate_security_standards(OUTPUT_DIR.parent / "CSIRO_Security_Standards_2026.pdf")
    
    years = [2023, 2024, 2025]
    providers = [
        ("AWS", generate_aws_invoice, generate_aws_finops_report, generate_aws_service_agreement),
        ("Azure", generate_azure_invoice, generate_azure_finops_report, generate_azure_service_agreement),
        ("GCP", generate_gcp_invoice, generate_gcp_finops_report, generate_gcp_service_agreement),
    ]
    
    print(f"Orchestrating synthetic data generation in {OUTPUT_DIR}...")
    
    count = 0
    for year in years:
        for month in range(1, 13):
            date_str = date(year, month, 1).strftime("%Y-%m-%d")
            
            # Generate Monthly PDFs
            for name, gen_inv, gen_rep, _ in providers:
                inv_path = OUTPUT_DIR / f"{name}_Invoice_{year}_{month:02d}.pdf"
                rep_path = OUTPUT_DIR / f"{name}_FinOps_Report_{year}_{month:02d}.pdf"
                
                gen_inv(inv_path, date_str)
                gen_rep(rep_path, date_str)
                count += 2
            
            # Generate Monthly Consolidated CSV
            csv_path = OUTPUT_DIR / f"Consolidated_FinOps_Chargeback_{year}_{month:02d}.csv"
            generate_finops_csv(csv_path, year, month)
            count += 1
            
        # Generate Annual Service Agreements
        for name, _, _, gen_sa in providers:
            sa_path = OUTPUT_DIR / f"{name}_Service_Agreement_{year}.pdf"
            gen_sa(sa_path, f"{year}-01-01")
            count += 1
            
    print(f"Successfully generated {count} high-fidelity localized documents.")

if __name__ == "__main__":
    main()
