import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Risk and Issue Interactive Dashboard - Google",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for AI Studio look & feel
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Top Header Bar */
    .header-box {
        background-color: #ffffff;
        padding: 16px 24px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        font-size: 22px;
        font-weight: 700;
        color: #202124;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .update-badge {
        background-color: #f1f3f4;
        color: #5f6368;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* Stat Cards */
    .metric-card-red {
        background-color: #ffffff;
        border: 1px solid #fecaca;
        border-left: 6px solid #dc2626;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card-amber {
        background-color: #ffffff;
        border: 1px solid #fef08a;
        border-left: 6px solid #d97706;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-tag-red {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-tag-amber {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    
    /* Heatmap Grid Cell Base Styling */
    .hm-cell {
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: 700;
        color: #ffffff;
        position: relative;
        min-height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .hm-green-1 { background-color: #4caf50; }
    .hm-green-2 { background-color: #66bb6a; }
    .hm-green-3 { background-color: #81c784; }
    .hm-yellow-1 { background-color: #fff176; color: #374151; }
    .hm-yellow-2 { background-color: #ffee58; color: #374151; }
    .hm-orange-1 { background-color: #ffa726; }
    .hm-orange-2 { background-color: #fb8c00; }
    .hm-red-1 { background-color: #ef5350; }
    .hm-red-2 { background-color: #e53935; }
    
    .hm-circle {
        background-color: rgba(0, 0, 0, 0.25);
        color: #ffffff;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        margin-left: 6px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. MOCK DATASET CREATION (93 RISKS + 8 ISSUES = 101 TOTAL REGISTER)
# -----------------------------------------------------------------------------
@st.cache_data
def get_mock_data():
    today = datetime.now()
    d_minus_3 = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    d_minus_5 = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    d_minus_10 = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    d_minus_30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    categories = ["Cost", "Scope", "Schedule", "Governance Assurance", "Legal/Contract"]
    owners = ["Susan Allin", "Michael Maconachie", "Scott Deacon", "Tom Trobe", "Mick Devine"]
    driver_trees = [
        "1.10a Infrastructure Ready", 
        "1.10b Platform Ready", 
        "1.7a DevSecOps", 
        "Schedule 5 Governance", 
        "Export Compliance"
    ]

    risks = []
    # Seed specific detailed risks first
    risks.append({
        "ID": "R-0001",
        "Name": "Liability - unlimited liability for repudiation & default",
        "Owner": "Susan Allin",
        "Driver_Tree_Ref": "Schedule 5 Governance",
        "Category": "Cost",
        "Inherent_Likelihood": 5, "Inherent_Consequence": 5, "Inherent_Rating": "Extreme",
        "Residual_Likelihood": 3, "Residual_Consequence": 5, "Residual_Rating": "Critical",
        "Trend": "Same ↔", "Status": "Active", "Escalation_Status": "PSG",
        "Date_Raised": d_minus_30, "Date_Closed": None, "Last_Updated": d_minus_3,
        "Idle_Days": 3, "Description": "Unlimited liability cap for specific default clauses under Schedule 5."
    })
    risks.append({
        "ID": "R-0002",
        "Name": "Extensive audit rights for Monaro and ANAO",
        "Owner": "Michael Maconachie",
        "Driver_Tree_Ref": "1.10b Platform Ready",
        "Category": "Cost",
        "Inherent_Likelihood": 4, "Inherent_Consequence": 4, "Inherent_Rating": "Critical",
        "Residual_Likelihood": 3, "Residual_Consequence": 4, "Residual_Rating": "High",
        "Trend": "Same ↔", "Status": "Active", "Escalation_Status": "Internal Google",
        "Date_Raised": d_minus_5, "Date_Closed": None, "Last_Updated": d_minus_3,
        "Idle_Days": 3, "Description": "ANAO audit provisions requiring extensive record retrieval."
    })

    # Generate total 93 risks matching status counts: Active (75), Eventuated (18) -> Open (93 total)
    np.random.seed(42)
    for i in range(3, 94):
        status = "Active" if i <= 75 else "Eventuated"
        l_inh = np.random.randint(1, 6)
        c_inh = np.random.randint(1, 6)
        l_res = max(1, l_inh - np.random.randint(0, 2))
        c_res = max(1, c_inh - np.random.randint(0, 2))
        
        esc = np.random.choice(["Internal Google", "Team Google", "PSG", "IPF"], p=[0.45, 0.15, 0.35, 0.05])
        idle = np.random.randint(1, 15)
        
        risks.append({
            "ID": f"R-{i:04d}",
            "Name": f"Program Risk {i} - {np.random.choice(['Resource bottleneck', 'API latency', 'Governance delay', 'HW lead time'])}",
            "Owner": np.random.choice(owners),
            "Driver_Tree_Ref": np.random.choice(driver_trees),
            "Category": np.random.choice(categories),
            "Inherent_Likelihood": l_inh, "Inherent_Consequence": c_inh,
            "Inherent_Rating": "Extreme" if l_inh*c_inh >= 20 else ("High" if l_inh*c_inh>=12 else "Medium"),
            "Residual_Likelihood": l_res, "Residual_Consequence": c_res,
            "Residual_Rating": "Extreme" if l_res*c_res >= 20 else ("High" if l_res*c_res>=12 else "Medium"),
            "Trend": np.random.choice(["Better ↑", "Worse ↓", "Same ↔"], p=[0.3, 0.2, 0.5]),
            "Status": status,
            "Escalation_Status": esc,
            "Date_Raised": d_minus_3 if i == 15 else d_minus_30,
            "Date_Closed": None,
            "Last_Updated": d_minus_10 if idle > 7 else d_minus_3,
            "Idle_Days": idle,
            "Description": f"Detailed description for risk {i}."
        })

    # Generate 8 closed/additional risks to make total 101 register items
    for i in range(94, 102):
        risks.append({
            "ID": f"R-{i:04d}",
            "Name": f"Archived Risk {i}",
            "Owner": np.random.choice(owners),
            "Driver_Tree_Ref": np.random.choice(driver_trees),
            "Category": "Schedule",
            "Inherent_Likelihood": 2, "Inherent_Consequence": 2, "Inherent_Rating": "Low",
            "Residual_Likelihood": 1, "Residual_Consequence": 1, "Residual_Rating": "Low",
            "Trend": "Better ↑", "Status": "Closed", "Escalation_Status": "Internal Google",
            "Date_Raised": d_minus_30, "Date_Closed": d_minus_5, "Last_Updated": d_minus_5,
            "Idle_Days": 0, "Description": "Closed risk item."
        })

    issues = [
        {
            "ID": "I-0001", "Name": "Environment Ready platform config delay (GDC Enterprise E.01)",
            "Owner": "Tom Trobe", "Driver_Tree_Ref": "1.10b Platform Ready", "Category": "Schedule",
            "Severity_Rating": "Critical", "Trend": "Worse ↓", "Status": "Active", "Escalation_Status": "IPF",
            "Date_Raised": d_minus_5, "Date_Closed": None, "Last_Updated": d_minus_3,
            "Action_Plan": "Validating schedule impacts with CD1 Gap Closure Plan."
        },
        {
            "ID": "I-0002", "Name": "Delayed build of E01 due to product build quality issues",
            "Owner": "Scott Deacon", "Driver_Tree_Ref": "1.10b Platform Ready", "Category": "Schedule",
            "Severity_Rating": "Critical", "Trend": "Worse ↓", "Status": "Active", "Escalation_Status": "PSG",
            "Date_Raised": d_minus_3, "Date_Closed": None, "Last_Updated": d_minus_3,
            "Action_Plan": "Escalate with Product team for local delivery build support."
        },
        {
            "ID": "I-0003", "Name": "Lack of dedicated Export Control Officer resource",
            "Owner": "Mick Devine", "Driver_Tree_Ref": "Export Compliance", "Category": "Scope",
            "Severity_Rating": "Critical", "Trend": "Worse ↓", "Status": "Active", "Escalation_Status": "PSG",
            "Date_Raised": d_minus_3, "Date_Closed": None, "Last_Updated": d_minus_3,
            "Action_Plan": "Recruit dedicated EC resource."
        },
        {
            "ID": "I-0004", "Name": "GCP Environment O sandbox access delay for ACN",
            "Owner": "Scott Deacon", "Driver_Tree_Ref": "1.7a DevSecOps", "Category": "Schedule",
            "Severity_Rating": "High", "Trend": "Better ↑", "Status": "Active", "Escalation_Status": "Internal Google",
            "Date_Raised": d_minus_10, "Date_Closed": None, "Last_Updated": d_minus_3,
            "Action_Plan": "Provide platform support for ACN access."
        }
    ]

    driver_tree_meta = {
        "1.10a Infrastructure Ready": {
            "title": "1.10a Infrastructure Ready (GDC Enterprise)",
            "owner": "Tom Trobe", "status": "Green 🟢 - Hardware delivery completed.", "last_updated": d_minus_3
        },
        "1.10b Platform Ready": {
            "title": "1.10b Platform Ready (GDC Enterprise E.01)",
            "owner": "Tom Trobe / Scott Deacon", "status": "Red 🔴 - Critical build config delays.", "last_updated": d_minus_3
        },
        "1.7a DevSecOps": {
            "title": "1.7a DevSecOps Core (GCP O & Tenancy)",
            "owner": "Scott Deacon", "status": "Amber 🟡 - GCP O access resolved; build commenced.", "last_updated": d_minus_3
        },
        "Schedule 5 Governance": {
            "title": "Schedule 5 Governance & Contract Requirements",
            "owner": "Susan Allin / Michael Maconachie", "status": "Amber 🟡 - Liability caps under review.", "last_updated": d_minus_3
        },
        "Export Compliance": {
            "title": "Export Controls & ITAR Governance",
            "owner": "Mick Devine", "status": "Red 🔴 - Recruitment in progress.", "last_updated": d_minus_3
        }
    }

    return pd.DataFrame(risks), pd.DataFrame(issues), driver_tree_meta

df_risks, df_issues, driver_tree_meta = get_mock_data()

# -----------------------------------------------------------------------------
# 2. TOP DASHBOARD HEADER BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">
        <span>🚨 Risk and Issue Interactive Dashboard</span>
    </div>
    <div class="update-badge">
        ⏱️ DASHBOARD LAST UPDATED: <b>Risk Reg: 29 Jul 2026</b> &nbsp;|&nbsp; <b>Issue Reg: 29 Jul 2026</b>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs matching AI Studio Draft
tab_overview, tab_trends, tab_driver, tab_issues, tab_ledger = st.tabs([
    "📊 Overview Dashboard",
    "📈 Performance Trends",
    "🌳 CD1 Driver Tree",
    "⚠️ Issue Dashboard",
    "📋 Whole Register Ledger"
])

# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW DASHBOARD (DIRECT AI STUDIO REPLICATION)
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("5x5 Risk Heatmap (93 Risks)")
    st.caption("Tap any cell to inspect")
    
    # Filter Row: Pill Selector + Rating Mode
    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        status_view = st.radio(
            "Filter Status:",
            ["Open (93)", "Active (75)", "Eventuated (18)", "All (101)"],
            horizontal=True,
            index=0
        )
    with f_col2:
        rating_mode = st.radio(
            "Rating View:",
            ["Inherent", "Residual"],
            horizontal=True,
            index=1
        )

    # Filter dataset according to selection
    if "Active" in status_view:
        view_df = df_risks[df_risks["Status"] == "Active"]
    elif "Eventuated" in status_view:
        view_df = df_risks[df_risks["Status"] == "Eventuated"]
    elif "Open" in status_view:
        view_df = df_risks[df_risks["Status"].isin(["Active", "Eventuated"])]
    else:
        view_df = df_risks.copy()

    st.write("")
    
    # Top Highlight Cards above Heatmap
    c1, c2 = st.columns(2)
    with c1:
        extreme_count = len(view_df[(view_df["Residual_Consequence"] >= 4) & (view_df["Residual_Likelihood"] >= 4)])
        st.markdown(f"""
        <div class="metric-card-red">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 700; color: #991b1b;">🔴 EXTREME TOP RISKS</span>
                <span class="badge-tag-red">Score 23-25</span>
            </div>
            <div style="font-size: 28px; font-weight: 800; color: #111827; margin-top: 4px;">
                {extreme_count} <span style="font-size: 15px; font-weight: 500; color: #6b7280;">Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        idle_count = len(view_df[view_df["Idle_Days"] > 7])
        st.markdown(f"""
        <div class="metric-card-amber">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 700; color: #92400e;">🟡 IDLE / UNACTIONED RISKS</span>
                <span class="badge-tag-amber">>7 Days Idle</span>
            </div>
            <div style="font-size: 28px; font-weight: 800; color: #111827; margin-top: 4px;">
                {idle_count} <span style="font-size: 15px; font-weight: 500; color: #6b7280;">Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 5x5 HEATMAP MATRIX (REPLICATING SCREENSHOT MATRIX VALUES & CIRCLE BADGES)
    st.markdown("##### **Likelihood (Horizontal) vs Consequence (Vertical)**")
    
    # Exact matrix grid count definition matching screenshot:
    # Rows: 5-Catastrophic down to 1-Minor
    # Columns: 1-Rare to 5-Almost Certain
    matrix_data = [
        # Row 5 Catastrophic: [Rare, Improbable, Occasional, Probable, Almost Certain]
        [{"val": 12, "circle": 0, "color": "hm-green-1"}, {"val": 17, "circle": 0, "color": "hm-yellow-1"}, {"val": 22, "circle": 0, "color": "hm-orange-1"}, {"val": 24, "circle": 0, "color": "hm-red-1"}, {"val": 25, "circle": 0, "color": "hm-red-2"}],
        # Row 4 Critical
        [{"val": 11, "circle": 0, "color": "hm-green-1"}, {"val": 16, "circle": 1, "color": "hm-yellow-1"}, {"val": 20, "circle": 0, "color": "hm-orange-1"}, {"val": 21, "circle": 2, "color": "hm-orange-2"}, {"val": 23, "circle": 1, "color": "hm-red-1"}],
        # Row 3 Major
        [{"val": 6, "circle": 0, "color": "hm-green-2"}, {"val": 10, "circle": 1, "color": "hm-green-1"}, {"val": 15, "circle": 0, "color": "hm-yellow-1"}, {"val": 18, "circle": 2, "color": "hm-orange-1"}, {"val": 19, "circle": 0, "color": "hm-orange-2"}],
        # Row 2 Moderate
        [{"val": 4, "circle": 0, "color": "hm-green-2"}, {"val": 5, "circle": 1, "color": "hm-green-2"}, {"val": 9, "circle": 2, "color": "hm-green-1"}, {"val": 13, "circle": 3, "color": "hm-yellow-2"}, {"val": 14, "circle": 1, "color": "hm-yellow-2"}],
        # Row 1 Minor
        [{"val": 1, "circle": 0, "color": "hm-green-3"}, {"val": 2, "circle": 0, "color": "hm-green-3"}, {"val": 3, "circle": 0, "color": "hm-green-2"}, {"val": 7, "circle": 0, "color": "hm-green-1"}, {"val": 8, "circle": 1, "color": "hm-green-1"}]
    ]

    row_labels = ["Catastrophic", "Critical", "Major", "Moderate", "Minor"]
    col_labels = ["1 RARE", "2 IMPROBABLE", "3 OCCASIONAL", "4 PROBABLE", "5 ALMOST CERTAIN"]

    # Header row for matrix
    cols = st.columns([1.5, 2, 2, 2, 2, 2])
    cols[0].markdown("**Consequence ↓**")
    for idx, clab in enumerate(col_labels):
        cols[idx+1].markdown(f"<div style='text-align:center; font-size:12px; font-weight:700; color:#5f6368;'>{clab}</div>", unsafe_allow_html=True)

    # Matrix rows
    for r_idx, r_label in enumerate(row_labels):
        r_cols = st.columns([1.5, 2, 2, 2, 2, 2])
        r_cols[0].markdown(f"**{r_label}**")
        for c_idx in range(5):
            cell = matrix_data[r_idx][c_idx]
            circle_html = f"<span class='hm-circle'>{cell['circle']}</span>" if cell['circle'] > 0 else ""
            r_cols[c_idx+1].markdown(f"""
            <div class="hm-cell {cell['color']}">
                <span>{cell['val']}</span>{circle_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 12px;'>← Likelihood Axis (Horizontal) | Consequence Axis (Vertical) →</div>", unsafe_allow_html=True)
    st.markdown("---")

    # KEY HIGHLIGHTS SECTION (LAST 7 DAYS)
    st.subheader("✨ Key Highlights")
    st.caption("Last 7 Days")

    h1, h2, h3, h4 = st.columns([1, 1, 1, 1.4])
    with h1:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:16px;">
            <div style="font-size:11px; font-weight:700; color:#6b7280;">DATE RAISED (LAST 7 DAYS) 🔗</div>
            <div style="font-size:24px; font-weight:800; color:#111827; margin-top:6px;">1 <span style="font-size:13px; font-weight:500; color:#374151;">Raised in Last 7 Days</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with h2:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:16px;">
            <div style="font-size:11px; font-weight:700; color:#6b7280;">DATE CLOSED (LAST 7 DAYS) 🔗</div>
            <div style="font-size:24px; font-weight:800; color:#111827; margin-top:6px;">0 <span style="font-size:13px; font-weight:500; color:#374151;">Closed in Last 7 Days</span></div>
        </div>
        """, unsafe_allow_html=True)

    with h3:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:16px;">
            <div style="font-size:11px; font-weight:700; color:#6b7280;">RISK LAST UPDATED (LAST 7 DAYS) 🔗</div>
            <div style="font-size:24px; font-weight:800; color:#111827; margin-top:6px;">0 <span style="font-size:13px; font-weight:500; color:#374151;">Updated in Last 7 Days</span></div>
        </div>
        """, unsafe_allow_html=True)

    with h4:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:16px;">
            <div style="font-size:11px; font-weight:700; color:#6b7280; margin-bottom:6px;">HIGHLIGHT TO / GOVERNANCE <span style="font-size:10px; color:#9ca3af;">Click cell to filter</span></div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:12px; font-weight:600;">
                <div>Internal Google: <span style="color:#2563eb;">9</span></div>
                <div>Team Google: <span style="color:#2563eb;">2</span></div>
                <div>PSG: <span style="color:#2563eb;">8</span></div>
                <div>IPF: <span style="color:#2563eb;">0</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: PERFORMANCE TRENDS
# -----------------------------------------------------------------------------
with tab_trends:
    st.subheader("📈 Performance Trends & Category Breakdown")
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("##### **Risk Category Distribution**")
        cat_counts = df_risks["Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        
        chart_cat = alt.Chart(cat_counts).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Category:N", sort="-y"),
            y="Count:Q",
            color=alt.Color("Category:N", scale=alt.Scale(scheme="category10"))
        ).properties(height=300)
        st.altair_chart(chart_cat, use_container_width=True)

    with t_col2:
        st.markdown("##### **Residual vs Inherent Risk Score Reduction**")
        df_risks["Inherent_Score"] = df_risks["Inherent_Likelihood"] * df_risks["Inherent_Consequence"]
        df_risks["Residual_Score"] = df_risks["Residual_Likelihood"] * df_risks["Residual_Consequence"]
        
        score_df = df_risks[["ID", "Inherent_Score", "Residual_Score"]].head(15).melt(id_vars=["ID"], var_name="Type", value_name="Score")
        chart_score = alt.Chart(score_df).mark_bar().encode(
            x=alt.X("ID:N"),
            y=alt.Y("Score:Q"),
            color=alt.Color("Type:N", scale=alt.Scale(range=["#ef5350", "#66bb6a"])),
            column=alt.Column("Type:N")
        ).properties(height=260, width=140)
        st.altair_chart(chart_score, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: CD1 DRIVER TREE EXPLORER
# -----------------------------------------------------------------------------
with tab_driver:
    st.subheader("🌳 CD1 Driver Tree Alignment")
    
    selected_driver = st.selectbox(
        "Select Driver Tree Section to Inspect:",
        options=list(driver_tree_meta.keys())
    )

    meta = driver_tree_meta[selected_driver]
    st.markdown(f"""
    <div style="background-color:#f0f7ff; border-left:6px solid #2563eb; padding:16px; border-radius:8px; margin-bottom:20px;">
        <h4 style="margin:0; color:#1e40af;">{meta['title']}</h4>
        <p style="margin:4px 0 0 0; color:#1e293b;"><b>Section Owner:</b> {meta['owner']} &nbsp;|&nbsp; <b>Last Updated:</b> {meta['last_updated']}</p>
        <p style="margin:6px 0 0 0; font-size:14px; color:#334155;"><b>Status:</b> {meta['status']}</p>
    </div>
    """, unsafe_allow_html=True)

    d_r1, d_r2 = st.columns(2)
    with d_r1:
        st.markdown("##### **Associated Risks**")
        driver_risks = df_risks[df_risks["Driver_Tree_Ref"] == selected_driver][["ID", "Name", "Owner", "Residual_Rating", "Trend"]]
        st.dataframe(driver_risks, use_container_width=True, hide_index=True)

    with d_r2:
        st.markdown("##### **Associated Issues**")
        driver_issues = df_issues[df_issues["Driver_Tree_Ref"] == selected_driver][["ID", "Name", "Owner", "Severity_Rating", "Trend"]]
        st.dataframe(driver_issues, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TAB 4: ISSUE DASHBOARD
# -----------------------------------------------------------------------------
with tab_issues:
    st.subheader("⚠️ Issue Dashboard & Critical Escalations")
    
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.metric("Total Active Issues", len(df_issues[df_issues["Status"]=="Active"]))
    with ic2:
        st.metric("Critical Issues", len(df_issues[df_issues["Severity_Rating"]=="Critical"]), delta="+1 (7d)", delta_color="inverse")
    with ic3:
        st.metric("Escalated to PSG / IPF", len(df_issues[df_issues["Escalation_Status"].isin(["PSG", "IPF"])]))

    st.markdown("##### **Active Issues Register & Action Plans**")
    st.dataframe(
        df_issues[["ID", "Name", "Owner", "Category", "Severity_Rating", "Escalation_Status", "Trend", "Action_Plan"]],
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# TAB 5: WHOLE REGISTER LEDGER
# -----------------------------------------------------------------------------
with tab_ledger:
    st.subheader("📋 Whole Register Ledger (Risks & Issues)")
    
    l_col1, l_col2, l_col3 = st.columns(3)
    with l_col1:
        cat_select = st.multiselect("Category Filter", options=list(df_risks["Category"].unique()), default=list(df_risks["Category"].unique()))
    with l_col2:
        owner_select = st.multiselect("Owner Filter", options=list(df_risks["Owner"].unique()))
    with l_col3:
        status_select = st.multiselect("Status Filter", options=["Active", "Eventuated", "Closed"], default=["Active", "Eventuated"])

    filtered_ledger = df_risks[
        (df_risks["Category"].isin(cat_select)) &
        (df_risks["Status"].isin(status_select))
    ]
    if owner_select:
        filtered_ledger = filtered_ledger[filtered_ledger["Owner"].isin(owner_select)]

    st.dataframe(
        filtered_ledger[["ID", "Name", "Owner", "Category", "Driver_Tree_Ref", "Residual_Rating", "Escalation_Status", "Status", "Last_Updated"]],
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_ledger.to_csv(index=False)
    st.download_button(
        label="📥 Export Filtered Register to CSV",
        data=csv_data,
        file_name="risk_and_issue_register.csv",
        mime="text/csv"
    )
