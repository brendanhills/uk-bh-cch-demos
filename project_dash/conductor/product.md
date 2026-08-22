# Product Definition: F-DSE Program Governance & Risk Intelligence Platform

## Vision
The **F-DSE Program Governance & Risk Intelligence Platform** (Monaro Risk Dashboard) serves as the central executive decision cockpit and operational risk intelligence hub for the **Future Data Science Environment (F-DSE)**. It transforms fragmented weekly PDF reports, Google Sheets risk registers, and contractual milestones into interactive, real-time executive insights powered by Google Gemini 3.5 Pro.

## Target Audience & Stakeholders
- **Primary Business Customer & Stakeholder:** Allison Innes (`allins@google.com`) and executive governance leadership.
- **Technical & Program Leads:** Steve Deacon (`sdeacon@google.com`), Wayne Davis (`waynedavis@google.com`), and Brendan Hills (`brendanhills@google.com`).
- **Delivery & Governance Teams:** Program managers, risk owners, and engineering leads monitoring Level 2 Contractual Milestones.

## Mandatory Architectural & Operational Principles
1. **Turnkey Handover & Browser-Triggered Data Operations**:
   - The platform is designed for long-term ownership by a non-specialist governance team without requiring a dedicated "Admin" portal or CLI scripts.
   - **Interactive In-Dashboard Governance**: All critical data lifecycle actions — live Google Sheets synchronization, Google Drive weekly report detection & ingestion, Gemini AI executive briefing generation, and neural podcast synthesis — are triggered on-demand directly from the dashboard via the **Workspace Sync Modal** (`sheetsModal`) or feature cards.
   - When any team member opens the Sync modal or triggers an update, the backend pipeline runs the necessary synchronizations, regenerates snapshots, and updates all views in real time.
   - User onboarding and access management are performed directly in standard Google Groups (`monaro-risk-dev@google.com` / `monaro-risk-prod@google.com`).
2. **Defensive, Resilient Processing**:
   - Ingestion and data synchronization adapt gracefully to common variations in filenames, dates, and data formats.
   - Core dashboard capabilities remain fully operational with deterministic baseline summaries even if external AI APIs or network connections experience temporary disruptions.
3. **Cohesive, Unified Architecture**:
   - The codebase maintains a small, unified footprint with clear component responsibilities.
   - Backend operations are centralized into a single ingestion pipeline and a concise REST interface to keep the system simple to understand, audit, and maintain.
4. **Zero-Trust Security & Data Isolation**:
   - Access is secured by Google SSO via Identity-Aware Proxy (IAP).
   - Sensitive project datasets are decoupled from public showcase datasets (`?project=sample`), keeping confidential data protected while enabling safe demos.

## Key Features & Capabilities
1. **Executive Decision Briefing (Gemini 3.5 Pro)**: Exception-first synthesis, Top 3 Action items, Early Warning Sleeper Outliers, and Neural Australian Audio Briefing.
2. **Interactive 5×5 Risk Heatmap**: Dynamic Inherent vs. Residual matrix toggling, active focus rings, and 1-click citation jumps.
3. **Interactive Live Ingestion**: User-triggered Google Drive sync, PDF report ingestion, and snapshot persistence.
4. **Contractual Delivery (CD1) Horizon**: Milestone driver tree mapping contractual commitments to high-priority remediation plans.
5. **Multi-Notebook Knowledge Base**: Dynamic UI switcher and CLI sync for multiple Gemini Notebooks.
6. **Turnkey Handover**: Complete operator manual (`docs/HANDOVER_GUIDE.md`) allowing immediate, self-service handover to the team.
