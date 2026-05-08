#!/usr/bin/env python3
"""
Unified FinOps Chargeback CSV Generator
Generates synthetic cloud cost and usage data for AWS, Azure, and GCP.
"""

import csv
import random
import os
from datetime import date

PROVIDERS = {
    "AWS": {
        "accounts": ["CSIRO-AWS-PROD-01", "CSIRO-AWS-DEV-02"],
        "services": [
            ("AmazonEC2", "Compute"),
            ("AmazonS3", "Storage"),
            ("AWSLambda", "Serverless"),
            ("AmazonRDS", "Database"),
            ("AmazonDynamoDB", "Database"),
        ]
    },
    "Azure": {
        "accounts": ["CSIRO-AZ-CORE-SUBS", "CSIRO-AZ-DATA61-SUBS"],
        "services": [
            ("Virtual Machines", "Compute"),
            ("Blob Storage", "Storage"),
            ("Azure Functions", "Serverless"),
            ("SQL Database", "Database"),
            ("Cosmos DB", "Database"),
        ]
    },
    "GCP": {
        "accounts": ["csiro-gcp-ag-prod", "csiro-gcp-ag-dev"],
        "services": [
            ("Compute Engine", "Compute"),
            ("Cloud Storage", "Storage"),
            ("Cloud Functions", "Serverless"),
            ("Cloud SQL", "Database"),
            ("BigQuery", "Analytics"),
        ]
    }
}

def generate_finops_csv(file_path, year, month):
    """Generates a synthetic FinOps chargeback CSV for a given month."""
    date_str = date(year, month, 1).strftime("%Y-%m-%d")
    
    header = ["Date", "Provider", "AccountID", "ServiceID", "ServiceName", "ResourceID", "Currency", "Cost"]
    
    rows = []
    
    for provider_name, info in PROVIDERS.items():
        for account in info["accounts"]:
            for svc_name, svc_cat in info["services"]:
                # Generate 1-3 entries per service per account
                num_entries = random.randint(1, 3)
                for i in range(num_entries):
                    resource_id = f"{svc_name.lower()}-{os.urandom(3).hex()}"
                    cost = random.uniform(5.0, 500.0)
                    
                    rows.append({
                        "Date": date_str,
                        "Provider": provider_name,
                        "AccountID": account,
                        "ServiceID": svc_cat,
                        "ServiceName": svc_name,
                        "ResourceID": resource_id,
                        "Currency": "AUD",
                        "Cost": f"{cost:.2f}"
                    })
    
    # Randomly shuffle rows to mimic real-world unsorted logs
    random.shuffle(rows)
    
    with open(file_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    generate_finops_csv("finops_sample.csv", 2026, 5)
