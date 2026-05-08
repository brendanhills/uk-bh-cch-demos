# Data Schema Mapping: Cloud Agent (CSIRO TDA)

This document provides the schema mapping and citation examples for the Cloud Agent to ensure accuracy when querying the Static Truth.

## 1. Consolidated FinOps Chargeback (CSV)
**File:** `Consolidated_FinOps_Chargeback_YYYY_MM.csv`

| Column | Description | Example Value |
| :--- | :--- | :--- |
| **Date** | Billing month start date | 2025-05-01 |
| **Provider** | Cloud Service Provider | AWS, Azure, GCP |
| **AccountID** | Unique CSIRO account identifier | CSIRO-AWS-PROD-01 |
| **ServiceID** | high-level category (Compute, Storage, etc) | Compute |
| **ServiceName** | Specific service name | AmazonEC2 |
| **ResourceID** | Unique ID for the specific resource | amazonec2-f3a2b1 |
| **Currency** | Currency for the Cost field | AUD |
| **Cost** | Monthly spend (GST exclusive) | 450.25 |

### Citation Example (CSV)
> "The EC2 spend for account PROD-01 was AUD 450.25 [CSV Row: amazonec2-f3a2b1]."

---

## 2. Invoices (PDF)
**Files:** `<Provider>_Invoice_YYYY_MM.pdf`

| Section | Key Data Points |
| :--- | :--- |
| **Invoice Details** | Document ID, Customer ID, Date |
| **Billing Period** | Exact start and end dates |
| **Summary of Charges** | Itemized list of services, Subtotal, GST (10%), TOTAL DUE |

### Citation Example (PDF Invoice)
> "AWS Invoice GCP-INV-A1B2 (May 2025) confirms a total GST amount of AUD 124.50 [AWS Invoice, May 2025]."

---

## 3. FinOps Reports (PDF)
**Files:** `<Provider>_FinOps_Report_YYYY_MM.pdf`

| Section | Metrics |
| :--- | :--- |
| **Spend & Trend Analysis** | Amortized Spend, Budget Variance (%), Commitment Coverage (%) |
| **Service-Level Detail** | Monthly spend per service and MoM % change |
| **Optimization Insights** | Rightsizing, Waste Management, and Savings Plan recommendations |

### Citation Example (PDF FinOps Report)
> "The Azure FinOps Report for June 2024 indicates a 12% MoM increase in SQL Database spend [Azure FinOps Report, June 2024]."

---

## 4. Service Agreements (PDF)
**Files:** `<Provider>_Service_Agreement_YYYY.pdf`

| Section | Key Terms |
| :--- | :--- |
| **1. Scope of Services** | Regions covered, supported services |
| **3. Security & Privacy** | Data residency, compliance standards (SOC2, ISO) |
| **5. Payment & Taxes** | AUD currency, GST compliance |
| **11. Miscellaneous** | Governing Law (NSW, Australia), Force Majeure |

### Citation Example (PDF Service Agreement)
> "Clause 11.3 of the AWS Customer Agreement specifies New South Wales as the governing jurisdiction [AWS Service Agreement, p. 7]."
