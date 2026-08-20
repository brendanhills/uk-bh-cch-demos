# Product Definition: F-DSE Program Governance & Risk Intelligence Platform

## Vision
The **F-DSE Program Governance & Risk Intelligence Platform** (Monaro Risk Dashboard) serves as the central executive decision cockpit and operational risk intelligence hub for the **Future Data Science Environment (F-DSE)**. It transforms fragmented weekly PDF reports, Google Sheets risk registers, and contractual milestones into interactive, real-time executive insights powered by Google Gemini 3.5 Pro.

## Target Audience & Stakeholders
- **Primary Business Customer & Stakeholder:** Allison Innes (`allins@google.com`) and executive governance leadership.
- **Technical & Program Leads:** Steve Deacon (`sdeacon@google.com`), Wayne Davis (`waynedavis@google.com`), and Brendan Hills (`brendanhills@google.com`).
- **Delivery & Governance Teams:** Program managers, risk owners, and engineering leads monitoring Level 2 Contractual Milestones.

## Mandatory Architectural & Security Invariants
1. **Zero-Trust Cloud Run Deployment & Google SSO**: Deployed on Google Cloud Run secured by Identity-Aware Proxy (IAP) for automated corporate Google SSO authentication (`monaro-risk-dev@google.com` and `monaro-risk-prod@google.com`).
2. **Drive-Native Data-Layer Access Restriction**: User access restriction is enforced at the Google Workspace / Google Drive shared folder and Google Groups level via Ganpati permissions (`monaro-risk-prod` and `monaro-risk-dev`).
3. **Turnkey Low-Maintenance Handover**: Automated CI/CD deployment via Google Cloud Build with group-based access management requiring zero manual container or IAM configuration for ongoing access administration.

## Key Features & Capabilities
1. **Executive Decision Briefing (Gemini 3.5 Pro)**: Exception-first synthesis, Top 3 Action items, Early Warning Sleeper Outliers, and Neural Australian Audio Briefing.
2. **Interactive 5×5 Risk Heatmap**: Dynamic Inherent vs. Residual matrix toggling, active focus rings, and 1-click citation jumps.
3. **Interactive Live Ingestion**: User-triggered Google Drive sync, PDF report ingestion, and snapshot persistence.
4. **Contractual Delivery (CD1) Horizon**: Milestone driver tree mapping contractual commitments to high-priority remediation plans.
5. **Multi-Notebook Knowledge Base**: Dynamic UI switcher and CLI sync for multiple Gemini Notebooks.
6. **Turnkey Handover**: Complete operator manual (`docs/HANDOVER_GUIDE.md`) allowing immediate, self-service handover to the team.
