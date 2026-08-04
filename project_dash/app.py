import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Project Dashboard - F-DSE Program",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 1. IN-MEMORY MOCK DATASETS & CATEGORY NORMALIZATION
# -----------------------------------------------------------------------------

@st.cache_data
def get_mock_data():
    today = datetime.now()
    d_minus_3 = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    d_minus_5 = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    d_minus_10 = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    d_minus_30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    risks = [
        {
            "ID": "R-0001",
            "Name": "Liability - unlimited liability for repudiation & default",
            "Owner": "Susan Allin",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Raw_Category": "Governance Assurance",
            "Category": "Cost",
            "Inherent_Likelihood": 3,
            "Inherent_Consequence": 5,
            "Inherent_Rating": "Critical",
            "Residual_Likelihood": 2,
            "Residual_Consequence": 4,
            "Residual_Rating": "High",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Critical_Update_7d": "Ongoing review of liability caps with legal and CoA governance.",
            "Description": "Unlimited liability for some losses (repudiation, wilful default) and high caps for confidentiality/privacy."
        },
        {
            "ID": "R-0002",
            "Name": "Extensive audit rights for Monaro and ANAO",
            "Owner": "Michael Maconachie",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Raw_Category": "Legal/Contract",
            "Category": "Cost",
            "Inherent_Likelihood": 4,
            "Inherent_Consequence": 4,
            "Inherent_Rating": "Critical",
            "Residual_Likelihood": 3,
            "Residual_Consequence": 4,
            "Residual_Rating": "High",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_5,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Critical_Update_7d": "ANAO audit briefings held with controllership; draft instructions published.",
            "Description": "Extensive audit rights for Monaro and government bodies like the Australian National Audit Office."
        },
        {
            "ID": "R-0003",
            "Name": "Onerous governance and reporting provisions",
            "Owner": "Susan Allin",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Raw_Category": "Scope",
            "Category": "Scope",
            "Inherent_Likelihood": 5,
            "Inherent_Consequence": 3,
            "Inherent_Rating": "High",
            "Residual_Likelihood": 3,
            "Residual_Consequence": 2,
            "Residual_Rating": "Medium",
            "Trend": "Better ↑",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_5,
            "Critical_Update_7d": None,
            "Description": "Contract Schedule 5 mandates heavyweight, CoA-driven governance framework."
        },
        {
            "ID": "R-0004",
            "Name": "Compliance with extensive Commonwealth Policies",
            "Owner": "Michael Maconachie",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Raw_Category": "Legal/Contract",
            "Category": "Cost",
            "Inherent_Likelihood": 3,
            "Inherent_Consequence": 3,
            "Inherent_Rating": "Medium",
            "Residual_Likelihood": 2,
            "Residual_Consequence": 2,
            "Residual_Rating": "Low",
            "Trend": "Better ↑",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_3,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Critical_Update_7d": None,
            "Description": "Policies can change; Defence required to provide notice and review within 90 days."
        },
        {
            "ID": "R-0005",
            "Name": "Individual Confidentiality Deed Polls required for personnel",
            "Owner": "Michael Maconachie",
            "Driver_Tree_Ref": "1.10a Infrastructure Ready",
            "Raw_Category": "Legal/Contract",
            "Category": "Schedule",
            "Inherent_Likelihood": 5,
            "Inherent_Consequence": 2,
            "Inherent_Rating": "Medium",
            "Residual_Likelihood": 2,
            "Residual_Consequence": 2,
            "Residual_Rating": "Low",
            "Trend": "Better ↑",
            "Status": "Closed",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": d_minus_5,
            "Last_Updated": d_minus_5,
            "Critical_Update_7d": None,
            "Description": "Individual Confidentiality Deed Polls required to allow any Google personnel access to CI."
        },
        {
            "ID": "R-0006",
            "Name": "Key Personnel commitments and retention (2.5 years)",
            "Owner": "Michael Maconachie",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Raw_Category": "Governance Assurance",
            "Category": "Schedule",
            "Inherent_Likelihood": 3,
            "Inherent_Consequence": 2,
            "Inherent_Rating": "Medium",
            "Residual_Likelihood": 2,
            "Residual_Consequence": 2,
            "Residual_Rating": "Low",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_10,
            "Critical_Update_7d": None,
            "Description": "Key Personnel obligations require Google to commit named resources for 2.5 years."
        },
        {
            "ID": "R-0007",
            "Name": "Extensive Monaro remediation rights for defects/breaches",
            "Owner": "Michael Maconachie",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Raw_Category": "Legal/Contract",
            "Category": "Scope",
            "Inherent_Likelihood": 2,
            "Inherent_Consequence": 4,
            "Inherent_Rating": "High",
            "Residual_Likelihood": 1,
            "Residual_Consequence": 3,
            "Residual_Rating": "Low",
            "Trend": "Better ↑",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_10,
            "Critical_Update_7d": None,
            "Description": "Extensive Monaro remediation rights for defects/breaches and step-in rights for cyber/security incidents."
        },
        {
            "ID": "R-0008",
            "Name": "Risk of Google 'lock in' for 7 years",
            "Owner": "Michael Maconachie",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Raw_Category": "Contract & Legal",
            "Category": "Scope",
            "Inherent_Likelihood": 1,
            "Inherent_Consequence": 5,
            "Inherent_Rating": "High",
            "Residual_Likelihood": 1,
            "Residual_Consequence": 5,
            "Residual_Rating": "Medium",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_3,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Critical_Update_7d": None,
            "Description": "Extensive Monaro termination rights and no right for Google to discontinue GDC AG for 7 years."
        }
    ]

    issues = [
        {
            "ID": "I-0003",
            "Name": "Environment Ready platform config delay (GDC Enterprise E.01)",
            "Owner": "Tom Trobe",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Trend": "Worse ↓",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_5,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Action_Plan": "Validating schedule impacts with CD1 Gap Closure Plan and mitigating delivery approach."
        },
        {
            "ID": "I-0004",
            "Name": "Delayed build of E01 due to product build quality issues",
            "Owner": "Scott Deacon",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Trend": "Worse ↓",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_3,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Action_Plan": "Drive escalation with Product team in support of local delivery build team to rapidly enable E01."
        },
        {
            "ID": "I-0006",
            "Name": "GCP Environment O sandbox access delay for ACN",
            "Owner": "Scott Deacon",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "High",
            "Trend": "Better ↑",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_10,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Action_Plan": "Platform with ACN now, providing support to ensure they have access to deliver on required expectations."
        },
        {
            "ID": "I-0007",
            "Name": "DevSecOps (O) Core readiness delay",
            "Owner": "Tom Trobe",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_5,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Action_Plan": "I-129 Delivered. Platform successfully validated and environment build commenced."
        },
        {
            "ID": "I-0011",
            "Name": "Lack of dedicated Export Control Officer resource",
            "Owner": "Mick Devine",
            "Driver_Tree_Ref": "Export Compliance",
            "Raw_Category": "Prime Governance",
            "Category": "Scope",
            "Severity_Rating": "Critical",
            "Trend": "Worse ↓",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_3,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Action_Plan": "Onboard dedicated EC resource with appropriate knowledge and experience. Xwf recruitment in progress."
        },
        {
            "ID": "I-0012",
            "Name": "Low quality Integrated Master Schedule",
            "Owner": "Mick Devine",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "High",
            "Trend": "Better ↑",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_10,
            "Action_Plan": "Work with Accenture to ensure the right level of focus and activity occurs on schedule development."
        },
        {
            "ID": "I-0014",
            "Name": "CD1/CD1.5 definitions unclear in Schedule 2A",
            "Owner": "Scott Deacon",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Raw_Category": "Governance Assurance",
            "Category": "Scope",
            "Severity_Rating": "High",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_10,
            "Action_Plan": "Sync with Accenture to ensure aligned understanding of initialising capability and update Schedule 2A."
        },
        {
            "ID": "I-0001",
            "Name": "Platform Ready Test/Dev environment delay (E.01)",
            "Owner": "Tom Trobe",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "High",
            "Trend": "Better ↑",
            "Status": "Closed",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": d_minus_5,
            "Last_Updated": d_minus_5,
            "Action_Plan": "Resolved via CD1 Gap Closure Plan."
        },
        {
            "ID": "I-0010",
            "Name": "Delayed W.01 hardware delivery to country",
            "Owner": "Tom Trobe",
            "Driver_Tree_Ref": "1.10a Infrastructure Ready",
            "Raw_Category": "Schedule",
            "Category": "Schedule",
            "Severity_Rating": "Medium",
            "Trend": "Same ↔",
            "Status": "Closed",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_30,
            "Date_Closed": d_minus_5,
            "Last_Updated": d_minus_5,
            "Action_Plan": "Hardware delivery completed and verified."
        }
    ]

    driver_tree_meta = {
        "1.10a Infrastructure Ready": {
            "title": "1.10a Infrastructure Ready (GDC Enterprise)",
            "owner": "Tom Trobe",
            "status": "Green 🟢 - Hardware delivery completed. E.01 initial infrastructure provisioning ready.",
            "last_updated": d_minus_3
        },
        "1.10b Platform Ready": {
            "title": "1.10b Platform Ready (GDC Enterprise E.01)",
            "owner": "Tom Trobe / Scott Deacon",
            "status": "Red 🔴 - Critical build quality and config delays impacting E01 platform readiness. CD1 Gap Closure Plan active.",
            "last_updated": d_minus_3
        },
        "1.7a DevSecOps": {
            "title": "1.7a DevSecOps Core (GCP O & Tenancy)",
            "owner": "Scott Deacon / Tom Trobe",
            "status": "Amber 🟡 - GCP O sandbox access resolved for ACN; DevSecOps Core build commenced.",
            "last_updated": d_minus_3
        },
        "Schedule 5 Governance": {
            "title": "Schedule 5 Governance & Commonwealth Contractual Requirements",
            "owner": "Susan Allin / Michael Maconachie",
            "status": "Amber 🟡 - Onerous reporting requirements and unlimited liability caps under active review with legal.",
            "last_updated": d_minus_3
        },
        "Export Compliance": {
            "title": "Export Controls & ITAR Governance (Bundle B)",
            "owner": "Mick Devine",
            "status": "Red 🔴 - Dedicated Google Export Control Officer recruitment in progress to oversee export compliance.",
            "last_updated": d_minus_3
        }
    }

    df_risks = pd.DataFrame(risks)
    df_issues = pd.DataFrame(issues)
    return df_risks, df_issues, driver_tree_meta

df_risks, df_issues, driver_tree_meta = get_mock_data()

# Active filters for main KPI counts
active_risks = df_risks[df_risks["Status"] == "Active"]
active_issues = df_issues[df_issues["Status"] == "Active"]

# -----------------------------------------------------------------------------
# 2. SIDEBAR CONTROLS & BRANDING
# -----------------------------------------------------------------------------
st.sidebar.title("🛡️ F-DSE Program")
st.sidebar.caption("Spec-Driven UI Mockup • Phase 1 Prototype")
st.sidebar.markdown("---")

st.sidebar.subheader("🔍 Global Filters")
category_filter = st.sidebar.multiselect(
    "Category Filter",
    options=["Cost", "Scope", "Schedule", "Other"],
    default=["Cost", "Scope", "Schedule", "Other"],
)
owner_filter = st.sidebar.multiselect(
    "Owner Filter",
    options=sorted(list(set(active_risks["Owner"]).union(set(active_issues["Owner"])))),
    default=[],
    help="Leave empty to display all owners."
)

# Apply Sidebar Filters
filtered_risks = active_risks[active_risks["Category"].isin(category_filter)]
filtered_issues = active_issues[active_issues["Category"].isin(category_filter)]
if owner_filter:
    filtered_risks = filtered_risks[filtered_risks["Owner"].isin(owner_filter)]
    filtered_issues = filtered_issues[filtered_issues["Owner"].isin(owner_filter)]

st.sidebar.markdown("---")
st.sidebar.info("💡 **Prototype Note:** This dashboard uses realistic in-memory mock data for team review.")

# -----------------------------------------------------------------------------
# 3. HEADER & KPI OVERVIEW CARDS (OVERALL POSITION)
# -----------------------------------------------------------------------------
st.title("📊 Project Dashboard: Overall Risk & Issue Position")
st.markdown("Executive overview of program risks, critical issues, category heatmaps, and Driver Tree alignment.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔴 Total Active Risks",
        value=len(filtered_risks),
        delta="-1 (Closed 7d)",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="⚠️ Total Open Issues",
        value=len(filtered_issues),
        delta="+2 (New 7d)",
        delta_color="inverse"
    )

with col3:
    critical_risks_count = len(filtered_risks[filtered_risks["Residual_Rating"] == "Critical"])
    critical_issues_count = len(filtered_issues[filtered_issues["Severity_Rating"] == "Critical"])
    st.metric(
        label="🚨 Critical Items (Risks + Issues)",
        value=critical_risks_count + critical_issues_count,
        delta="0 (Same 7d)",
        delta_color="off"
    )

with col4:
    st.markdown("### 📈 Overall Trajectory")
    st.markdown("#### **`Better ↑`** • Stable")
    st.caption("Net improvements in Scope & Schedule ratings")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. CATEGORY HEATMAP & DISTRIBUTION (COST / SCOPE / SCHEDULE)
# -----------------------------------------------------------------------------
st.subheader("🔥 Overall Position: Risk Heatmap & Category Breakdown")

h_col1, h_col2 = st.columns([1.3, 1])

with h_col1:
    st.markdown("#### **5x5 Risk Matrix Heatmap**")
    matrix_mode = st.radio("Select Rating Mode:", ["Residual Risk", "Inherent Risk"], horizontal=True)
    
    # Build 5x5 Grid for Plotly
    like_col = "Residual_Likelihood" if matrix_mode == "Residual Risk" else "Inherent_Likelihood"
    cons_col = "Residual_Consequence" if matrix_mode == "Residual Risk" else "Inherent_Consequence"
    
    grid = pd.DataFrame(0, index=[5, 4, 3, 2, 1], columns=[1, 2, 3, 4, 5])
    for _, row in filtered_risks.iterrows():
        l = row[like_col]
        c = row[cons_col]
        if l in grid.index and c in grid.columns:
            grid.loc[l, c] += 1
            
    fig_heat = px.imshow(
        grid,
        labels=dict(x="Consequence (1-Minor to 5-Critical)", y="Likelihood (1-Rare to 5-Almost Certain)", color="Risk Count"),
        x=["1 - Minor", "2 - Moderate", "3 - Significant", "4 - Major", "5 - Critical"],
        y=["5 - Almost Certain", "4 - Probable", "3 - Occasional", "2 - Improbable", "1 - Rare"],
        color_continuous_scale="Reds",
        text_auto=True,
        aspect="auto"
    )
    fig_heat.update_layout(height=340, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_heat, use_container_width=True)

with h_col2:
    st.markdown("#### **Items by Normalized Category**")
    r_cat = filtered_risks["Category"].value_counts().rename("Active Risks")
    i_cat = filtered_issues["Category"].value_counts().rename("Open Issues")
    df_cat = pd.concat([r_cat, i_cat], axis=1).fillna(0).reset_index()
    df_cat.columns = ["Category", "Active Risks", "Open Issues"]
    
    fig_bar = px.bar(
        df_cat,
        x="Category",
        y=["Active Risks", "Open Issues"],
        barmode="group",
        color_discrete_sequence=["#EF5350", "#FFB74D"],
        labels={"value": "Count", "variable": "Item Type"}
    )
    fig_bar.update_layout(height=340, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. TOP 5 CRITICAL ISSUES & TOP 5 CRITICAL RISKS
# -----------------------------------------------------------------------------
st.subheader("🎯 Top 5 Critical Items by Rating")

t_col1, t_col2 = st.columns(2)

with t_col1:
    st.markdown("#### **🔥 Top 5 Risks based on Criticality**")
    top_5_risks = filtered_risks.sort_values(
        by=["Residual_Consequence", "Residual_Likelihood"], ascending=[False, False]
    ).head(5)
    
    display_risks = top_5_risks[["ID", "Name", "Owner", "Category", "Residual_Rating", "Trend"]]
    st.dataframe(
        display_risks,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Name": st.column_config.TextColumn("Risk Name", width="medium"),
            "Residual_Rating": st.column_config.TextColumn("Rating", width="small"),
            "Trend": st.column_config.TextColumn("Trend", width="small"),
        }
    )

with t_col2:
    st.markdown("#### **🚨 Top 5 Issues based on Criticality**")
    # Rank severity: Critical > High > Medium > Low
    severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    filtered_issues_sorted = filtered_issues.copy()
    filtered_issues_sorted["Sev_Rank"] = filtered_issues_sorted["Severity_Rating"].map(severity_order)
    top_5_issues = filtered_issues_sorted.sort_values(by="Sev_Rank", ascending=False).head(5)
    
    display_issues = top_5_issues[["ID", "Name", "Owner", "Category", "Severity_Rating", "Trend"]]
    st.dataframe(
        display_issues,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Name": st.column_config.TextColumn("Issue Name", width="medium"),
            "Severity_Rating": st.column_config.TextColumn("Severity", width="small"),
            "Trend": st.column_config.TextColumn("Trend", width="small"),
        }
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. 7-DAY ACTIVITY & ESCALATION TRACKER
# -----------------------------------------------------------------------------
st.subheader("📅 7-Day Activity & Escalation Tracker")

tab1, tab2, tab3, tab4 = st.tabs([
    "🆕 Raised in Last 7 Days (Cost/Scope/Schedule)",
    "✅ Closed in Last 7 Days",
    "📢 Critical Risk Updates (Last 7 Days)",
    "🚀 Escalation Changes (Internal & IPF/PSG)"
])

with tab1:
    st.markdown("##### **New Risks & Issues Raised in Last 7 Days (by Category)**")
    new_risks = df_risks[df_risks["Date_Raised"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
    new_issues = df_issues[df_issues["Date_Raised"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        cost_items = len(new_risks[new_risks["Category"] == "Cost"]) + len(new_issues[new_issues["Category"] == "Cost"])
        st.metric("💰 Cost (7d New)", cost_items)
    with c_col2:
        scope_items = len(new_risks[new_risks["Category"] == "Scope"]) + len(new_issues[new_issues["Category"] == "Scope"])
        st.metric("📦 Scope (7d New)", scope_items)
    with c_col3:
        sched_items = len(new_risks[new_risks["Category"] == "Schedule"]) + len(new_issues[new_issues["Category"] == "Schedule"])
        st.metric("⏱️ Schedule (7d New)", sched_items)
        
    combined_new = pd.concat([
        new_risks[["ID", "Name", "Category", "Owner", "Date_Raised"]].assign(Type="Risk"),
        new_issues[["ID", "Name", "Category", "Owner", "Date_Raised"]].assign(Type="Issue")
    ])
    st.dataframe(combined_new, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("##### **Risks & Issues Closed in Last 7 Days**")
    closed_risks = df_risks[(df_risks["Status"] == "Closed") & (df_risks["Date_Closed"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))]
    closed_issues = df_issues[(df_issues["Status"] == "Closed") & (df_issues["Date_Closed"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))]
    
    combined_closed = pd.concat([
        closed_risks[["ID", "Name", "Category", "Owner", "Date_Closed"]].assign(Type="Risk"),
        closed_issues[["ID", "Name", "Category", "Owner", "Date_Closed"]].assign(Type="Issue")
    ])
    st.dataframe(combined_closed, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("##### **Updates in the Last Week for Risks Rated 'Critical'**")
    crit_risks_updates = df_risks[
        (df_risks["Inherent_Rating"] == "Critical") & 
        (df_risks["Last_Updated"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
    ][["ID", "Name", "Owner", "Last_Updated", "Critical_Update_7d"]]
    st.dataframe(crit_risks_updates, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("##### **Escalations Changed to 'Internal' or 'IPF/PSG' in Last 7 Days**")
    esc_risks = df_risks[df_risks["Escalation_Changed_7d"] == True][["ID", "Name", "Category", "Owner", "Escalation_Status"]].assign(Type="Risk")
    esc_issues = df_issues[df_issues["Escalation_Changed_7d"] == True][["ID", "Name", "Category", "Owner", "Escalation_Status"]].assign(Type="Issue")
    combined_esc = pd.concat([esc_risks, esc_issues])
    st.dataframe(combined_esc, use_container_width=True, hide_index=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. INTERACTIVE DRIVER TREE EXPLORER
# -----------------------------------------------------------------------------
st.subheader("🌲 Driver Tree Explorer")
st.markdown("Select a Driver Tree item to view the latest section status update and inspect assigned risks and issues.")

driver_options = ["All / Program Overview"] + list(driver_tree_meta.keys())
selected_node = st.selectbox(
    "**Select Driver Tree Section:**",
    options=driver_options,
    index=0
)

if selected_node == "All / Program Overview":
    st.info("💡 **Showing all Driver Tree sections.** Select a specific node above to drill into an individual section update.")
    tree_risks = filtered_risks
    tree_issues = filtered_issues
else:
    meta = driver_tree_meta[selected_node]
    st.markdown(f"#### **{meta['title']}**")
    st.markdown(f"- **Section Owners:** `{meta['owner']}`")
    st.markdown(f"- **Latest Status Update:** {meta['status']}")
    st.caption(f"Last updated: {meta['last_updated']}")
    
    tree_risks = filtered_risks[filtered_risks["Driver_Tree_Ref"] == selected_node]
    tree_issues = filtered_issues[filtered_issues["Driver_Tree_Ref"] == selected_node]

dt_col1, dt_col2 = st.columns(2)

with dt_col1:
    st.markdown(f"##### **Assigned Risks ({len(tree_risks)})**")
    st.dataframe(
        tree_risks[["ID", "Name", "Category", "Residual_Rating", "Owner"]],
        use_container_width=True,
        hide_index=True
    )

with dt_col2:
    st.markdown(f"##### **Assigned Issues ({len(tree_issues)})**")
    st.dataframe(
        tree_issues[["ID", "Name", "Category", "Severity_Rating", "Owner"]],
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("F-DSE Project Dashboard Prototype • Built with Streamlit • Conductor Track: `dashboard_prototype`")
