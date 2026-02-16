# Access Control Scenarios - Setup & Demo Guide

This guide ensures you can reproduce the 4 specific access control scenarios requested.

## 👥 1. User & Group Setup
Before uploading content, ensure these users exist in your Identity Provider (or are mapped correctly):

| Name | User Email | Role/Group |
|------|------------|------------|
| **Tim Trader** | `tim.trader@brendanhills.altostrat.com` | `Traders`, `Employees` |
| **Ben Banker** | `ben.banker@brendanhills.altostrat.com` | `InvestmentBanking`, `Employees` |
| **Harry HR** | `harry.hr@brendanhills.altostrat.com` | `HRManagers`, `Employees` |
| **Cathy Compliance** | `cathy.compliance@brendanhills.altostrat.com` | `ComplianceOfficers`, `Employees` |
| **Ivan IT** | `ivan.it@brendanhills.altostrat.com` | `ITSupport`, `ITAdmins`, `Employees` |
| **John Smith** | `john.smith@brendanhills.altostrat.com` | `Employees` |

> [!IMPORTANT]
> Ensure the **"Employees"** group (or "All Users") includes everyone.

## 📂 2. Drive Folder Structure & Permissions
Upload the generated `drive_content` folders to your Google Drive Data Source root. Apply permissions **strictly** as follows:

| Folder Path | Share With (View Access) |
|-------------|--------------------------|
| `Scenario_1_Trading_Policies/Shared_Trading_Policies/` | `Traders` (Tim), `InvestmentBanking` (Ben), `ComplianceOfficers` (Cathy) |
| `Scenario_1_Trading_Policies/IB_Confidential/` | `InvestmentBanking` (Ben), `ComplianceOfficers` (Cathy) |
| `Scenario_2_HR_Records/` | **Restricted** (Harry HR only) |
| `Scenario_2_HR_Records/John_Smith/` | *Inherit from parent + add John's manager if needed* |
| `Scenario_3_Compliance_Audits/` | `ComplianceOfficers` (Cathy) |
| `Scenario_4_IT_Support/General_Knowledge_Base/` | `Employees` (Everyone) |
| `Scenario_4_IT_Support/Admin_Procedures/` | `ITAdmins` (Ivan) |

> [!TIP]
> **Granular File Permissions**: For Scenario 1, if you want only IB to see IB policies, you might need to set file-level permissions or use subfolders. The `users.json` generated in the folders describes the *intended* logic.

## 🎬 3. Demo Walkthrough

### Scenario 1: Trader vs. Investment Banker
*Context: Separation of duties (Chinese Wall).*

1. **Login as Tim Trader** (`tim.trader`)
2. Search: `"client gift policy"`
   - ✅ **Expect**: `Global_Trading_Gifts_Policy.pdf`
   - ❌ **Expect NOT**: `Investment_Banking_Gifts_Policy.pdf` (If permissions set correctly)
3. **Login as Ben Banker** (`ben.banker`)
   - ✅ **Expect**: Both policies (or just his own, depending on setup).

### Scenario 2: HR Privacy
*Context: Manager searching for sensitive employee records.*

1. **Login as Harry HR** (`harry.hr`)
2. Search: `"termination process for John Smith"`
   - ✅ **Expect**: `Termination_Process_John_Smith.pdf`
3. **Login as Tim Trader** (`tim.trader`)
   - ❌ **Expect**: No results found.

### Scenario 3: Compliance vs. Conflict
*Context: Finding violations without revealing sensitive HR logs to the wrong people.*

1. **Login as Cathy Compliance** (`cathy.compliance`)
2. Search: `"trading violations"`
   - ✅ **Expect**: `Audit_Log_Trading_Violations_Q1.pdf` (Shows Tim's violation).
   - ❌ **Expect NOT**: `HR_Disciplinary_Record_Tim_Trader` (If it existed and was HR-only).

### Scenario 4: IT Support vs. Admin
*Context: Helpdesk seeking knowledge vs. Admin docs.*

1. **Login as Support Tech (John Smith or Tim)**
2. Search: `"password reset"`
   - ✅ **Expect**: `KB_Password_Reset_Instructions.pdf`
   - ❌ **Expect NOT**: `Workday_Backend_Admin_Guide.pdf`
3. **Login as Ivan IT** (`ivan.it`)
   - ✅ **Expect**: `Workday_Backend_Admin_Guide.pdf`

## 🛠 Troubleshooting
- If **Tim** sees **IB** docs: Check if `Scenario_1` folder is shared with `Everyone` or if Tim is in the IB group.
- If **Search** returns nothing: Ensure the Drive connector has synced (can take 5-15 mins).
