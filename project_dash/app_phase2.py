import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# PAGE CONFIG & DENSE INFORMATION STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Project Dashboard - Advanced Phase 2/3 Roadmap",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    h1 { font-size: 1.6rem !important; font-weight: 700 !important; margin-bottom: 0.2rem !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; margin-top: 0.6rem !important; margin-bottom: 0.3rem !important; }
    h3 { font-size: 1.05rem !important; font-weight: 600 !important; margin-top: 0.4rem !important; margin-bottom: 0.2rem !important; }
    
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 8px 12px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #495057 !important;
        text-transform: uppercase;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.4rem !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ADVANCED MOCK DATASET
# -----------------------------------------------------------------------------
@st.cache_data
def get_advanced_mock_data():
    today = datetime.now()
    weeks = [(today - timedelta(weeks=12-i)).strftime("Wk %U (%b %d)") for i in range(12)]
    historical_df = pd.DataFrame({
        "Week": weeks,
        "Active Risks": [14, 13, 13, 12, 11, 11, 10, 10, 9, 9, 8, 7],
        "Closed Risks (Cumulative)": [0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6, 7],
        "Open Issues": [12, 11, 10, 10, 9, 8, 8, 7, 7, 6, 6, 5],
        "Resolved Issues (Cumulative)": [2, 3, 4, 4, 5, 6, 6, 7, 7, 8, 8, 9]
    })

    risks = [
        {
            "ID": "R-0001",
            "Name": "Liability - unlimited liability for repudiation & default",
            "Owner": "Susan Allin",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Category": "Cost",
            "Residual_Rating": "Critical",
            "Open_Days": 265,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Aging_Outlier": True,
            "Target_Date": "2026-08-31",
            "Target_Status": "On Track",
            "Escalation": "IPF/PSG",
        },
        {
            "ID": "R-0002",
            "Name": "Extensive audit rights for Monaro and ANAO",
            "Owner": "Michael Maconachie",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Category": "Cost",
            "Residual_Rating": "High",
            "Open_Days": 265,
            "Days_Since_Update": 18,
            "Stale_SLA": True,
            "Aging_Outlier": True,
            "Target_Date": "2026-08-15",
            "Target_Status": "Overdue SLA Update",
            "Escalation": "Internal",
        },
        {
            "ID": "R-0003",
            "Name": "Onerous governance and reporting provisions",
            "Owner": "Susan Allin",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Category": "Scope",
            "Residual_Rating": "Medium",
            "Open_Days": 265,
            "Days_Since_Update": 5,
            "Stale_SLA": False,
            "Aging_Outlier": True,
            "Target_Date": "2026-09-30",
            "Target_Status": "On Track",
            "Escalation": "Internal",
        },
        {
            "ID": "R-0004",
            "Name": "Compliance with extensive Commonwealth Policies",
            "Owner": "Michael Maconachie",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Category": "Cost",
            "Residual_Rating": "Low",
            "Open_Days": 265,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Aging_Outlier": True,
            "Target_Date": "2026-10-15",
            "Target_Status": "On Track",
            "Escalation": "Internal",
        }
    ]

    issues = [
        {
            "ID": "I-0003",
            "Name": "Environment Ready platform config delay (GDC Enterprise E.01)",
            "Owner": "Tom Trobe",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Open_Days": 27,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Target_Date": "2026-08-10",
            "Escalation": "IPF/PSG",
        },
        {
            "ID": "I-0004",
            "Name": "Delayed build of E01 due to product build quality issues",
            "Owner": "Scott Deacon",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Open_Days": 5,
            "Days_Since_Update": 1,
            "Stale_SLA": False,
            "Target_Date": "2026-08-12",
            "Escalation": "IPF/PSG",
        },
        {
            "ID": "I-0007",
            "Name": "DevSecOps (O) Core readiness delay",
            "Owner": "Tom Trobe",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Open_Days": 5,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Target_Date": "2026-08-20",
            "Escalation": "Internal",
        },
        {
            "ID": "I-0011",
            "Name": "Lack of dedicated Export Control Officer resource",
            "Owner": "Mick Devine",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "Export Compliance",
            "Category": "Scope",
            "Severity_Rating": "Critical",
            "Open_Days": 3,
            "Days_Since_Update": 1,
            "Stale_SLA": False,
            "Target_Date": "2026-08-15",
            "Escalation": "IPF/PSG",
        }
    ]

    return historical_df, pd.DataFrame(risks), pd.DataFrame(issues)

historical_df, df_risks, df_issues = get_advanced_mock_data()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title("🚀 F-DSE Roadmap (Phase 2/3)")
view_selection = st.sidebar.radio(
    "Select View:",
    [
        "🤖 AI Executive Briefing Generator",
        "⏰ Aging & Stale SLA Radar",
        "👤 Owner & RACI Workload Matrix",
        "📈 12-Week Burn-Down & Trendlines",
        "🔗 Dependency & Blocker Network",
        "📄 One-Click Executive Deck Export"
    ],
    help="Select an advanced Google executive reporting capability."
)

# -----------------------------------------------------------------------------
# HEADER & HELP POPOVER
# -----------------------------------------------------------------------------
h_title_col, h_help_col = st.columns([4, 1])
with h_title_col:
    st.title("🚀 Advanced Governance & Roadmap Mockup")
with h_help_col:
    st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)
    with st.popover("❓ Roadmap Guide"):
        st.markdown("""
**Phase 2 & 3 Advanced Features Guide:**
- **AI Executive Briefing:** Auto-generates weekly summary blurbs for emails & g3docs.
- **SLA Radar:** Flags stale items (>14 days without comment) and aging risks (>180 open days).
- **RACI Workload:** Workload distribution by Risk/Issue Owner.
- **12-Week Trendline:** Historical trajectory showing program convergence over 12 weeks.
- **Dependency Graph:** Sankey diagram showing how critical blockers impact downstream milestones.
""")

# -----------------------------------------------------------------------------
# VIEW RENDERERS
# -----------------------------------------------------------------------------
if view_selection == "🤖 AI Executive Briefing Generator":
    st.subheader("🤖 AI-Assisted Weekly Executive Summary")
    with st.container(border=True):
        st.markdown("### 📋 Executive Summary (Week Ending 04 Aug 2026)")
        summary_md = """
> **F-DSE PROGRAM EXECUTIVE BRIEFING**
>
> 🟢 **1. Program Trajectory:** Overall trajectory is **Stable (Better ↑)**. Active risks stand at **5** (-1 closed 7d) and open critical issues at **4** (+2 new 7d).
> 🚨 **2. Critical Blockers (IPF/PSG):**
> - **Issue I-0004 (E01 Build Quality):** Escalated to **IPF/PSG**. Product build quality issues causing 5-day flow-on delay to Mission Support readiness (*1.10d*).
> - **Issue I-0011 (Export Compliance):** Escalated to **IPF/PSG**. Dedicated Google Export Control Officer recruitment is actively underway (*Mick Devine*).
> 🌲 **3. Milestone Focus:** *1.10a Infrastructure Ready* (Green 🟢); *1.7a DevSecOps* (Amber 🟡); *1.10b Platform Ready* (Red 🔴).
"""
        st.markdown(summary_md)
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📋 Copy Summary", help="Copy summary to clipboard"):
                st.toast("Copied!", icon="✅")
        with col2:
            st.download_button("📥 Download (.md)", summary_md, "FDSE_Executive_Summary.md", "text/markdown", help="Download markdown summary file")

elif view_selection == "⏰ Aging & Stale SLA Radar":
    st.subheader("⏰ Stale Item & Aging Risk Radar")
    stale_risks = df_risks[df_risks["Stale_SLA"] == True]
    aging_risks = df_risks[df_risks["Aging_Outlier"] == True]
    
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("⚠️ Stale SLA (>14d Update)", len(stale_risks), delta="Overdue SLA", delta_color="inverse", help="Items with no comment update in over 14 days.")
    with m2: st.metric("⏳ Aging Outliers (>180d Open)", len(aging_risks), delta="Review Needed", delta_color="off", help="Risks open for more than 180 days.")
    with m3: st.metric("✅ Compliant Items", len(df_risks) - len(stale_risks), delta="Up to Date", delta_color="normal", help="Items compliant with 14-day SLA.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("### 🚨 Overdue SLA Radar (>14 Days)")
            st.dataframe(stale_risks[["ID", "Name", "Owner", "Days_Since_Update", "Target_Status"]], use_container_width=True, hide_index=True, height=220)
    with col_b:
        with st.container(border=True):
            st.markdown("### 📊 Open Days Breakdown")
            fig_age = px.bar(df_risks, x="ID", y="Open_Days", color="Residual_Rating", text="Open_Days", color_discrete_map={"Critical": "#EF5350", "High": "#FF7043", "Medium": "#FFCA28", "Low": "#66BB6A"})
            fig_age.update_layout(height=220, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_age, use_container_width=True)

elif view_selection == "👤 Owner & RACI Workload Matrix":
    st.subheader("👤 Owner & RACI Workload Matrix")
    combined_owners = pd.concat([
        df_risks[["ID", "Name", "Owner", "RACI", "Residual_Rating", "Category"]].rename(columns={"Residual_Rating": "Rating"}).assign(Type="Risk"),
        df_issues[["ID", "Name", "Owner", "RACI", "Severity_Rating", "Category"]].rename(columns={"Severity_Rating": "Rating"}).assign(Type="Issue")
    ])
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        with st.container(border=True):
            st.markdown("### Workload Distribution by Owner")
            fig_raci = px.bar(combined_owners, x="Owner", color="Rating", barmode="stack", color_discrete_map={"Critical": "#D32F2F", "High": "#F57C00", "Medium": "#FBC02D", "Low": "#388E3C"})
            fig_raci.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_raci, use_container_width=True)
    with col2:
        with st.container(border=True):
            st.markdown("### RACI Accountability Table")
            st.dataframe(combined_owners[["ID", "Owner", "RACI", "Rating", "Type"]], use_container_width=True, hide_index=True, height=260)

elif view_selection == "📈 12-Week Burn-Down & Trendlines":
    st.subheader("📈 12-Week Historical Burn-Down & Trajectory")
    with st.container(border=True):
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=historical_df["Week"], y=historical_df["Active Risks"], mode="lines+markers", name="Active Risks", line=dict(color="#E53935", width=3)))
        fig_trend.add_trace(go.Scatter(x=historical_df["Week"], y=historical_df["Closed Risks (Cumulative)"], mode="lines+markers", name="Closed Risks", line=dict(color="#43A047", width=3, dash="dash")))
        fig_trend.add_trace(go.Scatter(x=historical_df["Week"], y=historical_df["Open Issues"], mode="lines+markers", name="Open Issues", line=dict(color="#FB8C00", width=3)))
        fig_trend.update_layout(height=380, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_trend, use_container_width=True)

elif view_selection == "🔗 Dependency & Blocker Network":
    st.subheader("🔗 Driver Tree Blocker Network Graph")
    with st.container(border=True):
        nodes = ["Issue I-0004", "Issue I-0003", "Risk R-0001", "Risk R-0002", "1.10b Platform Ready", "1.10c Env Ready", "1.10d Mission Support", "1.13 Milestone 2 (IBR)"]
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, label=nodes, color=["#E53935", "#E53935", "#FB8C00", "#FB8C00", "#1E88E5", "#1E88E5", "#1E88E5", "#43A047"]),
            link=dict(source=[0, 1, 2, 3], target=[6, 5, 7, 5], value=[1, 1, 1, 1])
        )])
        fig_sankey.update_layout(height=380, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_sankey, use_container_width=True)

elif view_selection == "📄 One-Click Executive Deck Export":
    st.subheader("📄 Executive Deck Export")
    with st.container(border=True):
        st.success("✅ Executive Snapshot generated!")
        st.download_button("📥 Export Executive PDF Deck (.pdf)", "PDF Mock Content", "FDSE_Executive_Deck.pdf", "application/pdf", help="Export current executive view to PDF deck")
        st.download_button("📊 Export Slide Deck (.pptx)", "PPTX Mock Content", "FDSE_Executive_Deck.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", help="Export to Google Slides / PowerPoint deck")

st.caption("F-DSE Advanced Program Reporting • Streamlit Port 9000 • Use ❓ Help for Guide")
