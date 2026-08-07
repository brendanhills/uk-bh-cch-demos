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
            "Target_Date": "2026-09-15",
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
            "Open_Days": 45,
            "Days_Since_Update": 21,
            "Stale_SLA": True,
            "Aging_Outlier": False,
            "Target_Date": "2026-10-01",
            "Target_Status": "Stale Update",
            "Escalation": "Internal",
        }
    ]

    blockers = [
        {"Source": "R-0001 (Liability Cap)", "Target": "1.10b Platform Build Sign-off", "Impact": "Legal Blocker"},
        {"Source": "I-0003 (Platform E01 Build)", "Target": "1.7a DevSecOps Core Access", "Impact": "Technical Dependency"},
        {"Source": "I-0011 (Export Control Officer)", "Target": "1.10a Hardware Delivery", "Impact": "Governance Blocker"},
        {"Source": "1.10b Platform Build Sign-off", "Target": "F-DSE Initializing Capability (CD1)", "Impact": "Milestone Blocker"}
    ]

    return historical_df, pd.DataFrame(risks), pd.DataFrame(blockers)

historical_df, df_risks, df_blockers = get_advanced_mock_data()

# -----------------------------------------------------------------------------
# HEADER & SIDEBAR
# -----------------------------------------------------------------------------
st.title("🚀 F-DSE Program Dashboard (Phase 2 & 3 Roadmap Prototype)")
st.caption("Operational & Governance Radar • Burn-Down Metrics • RACI Matrix • AI Executive Blurb Generator")

st.sidebar.title("🛡️ Governance Controls")
st.sidebar.markdown("---")
view_mode = st.sidebar.radio(
    "Select View Mode:",
    [
        "🔥 Stale & Aging Radar",
        "👥 RACI & Owner Load",
        "📉 12-Week Burn-Down",
        "🔗 Blocker Dependency Graph",
        "🤖 AI Executive Blurb"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Phase 2/3 Features:** Stale SLA (>14d update), Aging (>180d), Burn-Down trendlines, RACI matrix, Blocker graphs.")

# -----------------------------------------------------------------------------
# VIEW 1: STALE ITEM & AGING RADAR
# -----------------------------------------------------------------------------
if view_mode == "🔥 Stale & Aging Radar":
    st.subheader("🔥 Stale Item & Aging Radar (Open > 180 Days & Stale Updates)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("⚠️ Aging Outliers (>180 Days Open)", len(df_risks[df_risks["Aging_Outlier"]]))
    col2.metric("🚨 Stale SLA Items (>14d No Update)", len(df_risks[df_risks["Stale_SLA"]]))
    col3.metric("🎯 Total Monitored Risks", len(df_risks))

    st.markdown("##### **Aging & Stale Items Ledger**")
    st.dataframe(
        df_risks[["ID", "Name", "Owner", "Open_Days", "Days_Since_Update", "Stale_SLA", "Aging_Outlier", "Target_Date", "Target_Status"]],
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# VIEW 2: RACI & OWNER LOAD
# -----------------------------------------------------------------------------
elif view_mode == "👥 RACI & Owner Load":
    st.subheader("👥 Owner Accountability Matrix (RACI View)")
    
    raci_summary = df_risks.groupby(["Owner", "RACI"]).size().unstack(fill_value=0)
    st.dataframe(raci_summary, use_container_width=True)

# -----------------------------------------------------------------------------
# VIEW 3: 12-WEEK BURN-DOWN
# -----------------------------------------------------------------------------
elif view_mode == "📉 12-Week Burn-Down":
    st.subheader("📉 12-Week Historical Burn-Down & Convergence")
    
    fig = px.line(
        historical_df,
        x="Week",
        y=["Active Risks", "Open Issues", "Closed Risks (Cumulative)", "Resolved Issues (Cumulative)"],
        markers=True,
        title="12-Week Program Trajectory"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# VIEW 4: BLOCKER DEPENDENCY GRAPH
# -----------------------------------------------------------------------------
elif view_mode == "🔗 Blocker Dependency Graph":
    st.subheader("🔗 Cross-Bundle Blocker Dependency Graph")
    st.dataframe(df_blockers, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# VIEW 5: AI EXECUTIVE BLURB
# -----------------------------------------------------------------------------
elif view_mode == "🤖 AI Executive Blurb":
    st.subheader("🤖 AI-Assisted Weekly Executive Summary (Blurb Generator)")
    
    st.markdown("""
    > **Weekly Executive Summary (Auto-Generated from 7-Day Deltas):**
    > - **Scope & Governance:** Liability cap review ongoing for Schedule 5 clauses with legal and CoA governance.
    > - **Platform & Schedule:** Environment Ready E01 build delayed due to product build quality; CD1 Gap Closure Plan activated.
    > - **Resourcing & Escalations:** Export Control Officer recruitment in progress; escalated to PSG.
    """)
