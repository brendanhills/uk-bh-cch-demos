import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# PAGE CONFIG & HIGH-DENSITY DYNAMIC STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="F-DSE Project Dashboard (v1 & v2)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, .stButton, .stText {
        font-family: 'Google Sans', 'Roboto', -apple-system, sans-serif !important;
    }
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #202124 !important; margin-bottom: 0.2rem !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: #3c4043 !important; margin-top: 0.6rem !important; margin-bottom: 0.3rem !important; }
    h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #1a73e8 !important; margin-top: 0.4rem !important; margin-bottom: 0.2rem !important; }
    
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 8px 12px !important;
        box-shadow: 0 1px 2px rgba(60,64,67,0.06);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #202124 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #5f6368 !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.4rem !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# URL QUERY PARAMS & VERSION NAVIGATION
# -----------------------------------------------------------------------------
query_params = st.query_params
initial_version = query_params.get("version", query_params.get("v", "v1")).lower()
default_index = 1 if initial_version in ["v2", "2", "phase2", "roadmap"] else 0

selected_version = st.sidebar.radio(
    "📌 **Select Version / Path:**",
    ["v1: Phase 1 Baseline Mockup", "v2: Phase 2/3 Unified Dashboard (All Features)"],
    index=default_index,
    help="Switch between Baseline Customer Mockup (v1) and Full Unified Dashboard (v2). Direct URLs: ?version=v1 or ?version=v2"
)

current_v = "v1" if "v1" in selected_version else "v2"
st.query_params["version"] = current_v

st.sidebar.markdown("---")

# -----------------------------------------------------------------------------
# MOCK DATA GENERATOR
# -----------------------------------------------------------------------------
@st.cache_data
def get_mock_data():
    today = datetime.now()
    d_minus_3 = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    d_minus_5 = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    d_minus_10 = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    d_minus_30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")

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
            "Inherent_Likelihood": 3,
            "Inherent_Consequence": 5,
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
            "Open_Days": 265,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Aging_Outlier": True,
            "Target_Date": "2026-08-31",
            "Target_Status": "On Track",
            "Critical_Update_7d": "Ongoing review of liability caps with legal and CoA governance.",
        },
        {
            "ID": "R-0002",
            "Name": "Extensive audit rights for Monaro and ANAO",
            "Owner": "Michael Maconachie",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Category": "Cost",
            "Inherent_Likelihood": 4,
            "Inherent_Consequence": 4,
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
            "Open_Days": 265,
            "Days_Since_Update": 18,
            "Stale_SLA": True,
            "Aging_Outlier": True,
            "Target_Date": "2026-08-15",
            "Target_Status": "Overdue SLA Update",
            "Critical_Update_7d": "ANAO audit briefings held with controllership; draft instructions published.",
        },
        {
            "ID": "R-0003",
            "Name": "Onerous governance and reporting provisions",
            "Owner": "Susan Allin",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "Schedule 5 Governance",
            "Category": "Scope",
            "Inherent_Likelihood": 5,
            "Inherent_Consequence": 3,
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
            "Open_Days": 265,
            "Days_Since_Update": 5,
            "Stale_SLA": False,
            "Aging_Outlier": True,
            "Target_Date": "2026-09-30",
            "Target_Status": "On Track",
            "Critical_Update_7d": None,
        },
        {
            "ID": "R-0004",
            "Name": "Compliance with extensive Commonwealth Policies",
            "Owner": "Michael Maconachie",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Category": "Cost",
            "Inherent_Likelihood": 3,
            "Inherent_Consequence": 3,
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
            "Open_Days": 265,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Aging_Outlier": True,
            "Target_Date": "2026-10-15",
            "Target_Status": "On Track",
            "Critical_Update_7d": None,
        },
        {
            "ID": "R-0005",
            "Name": "Individual Confidentiality Deed Polls required for personnel",
            "Owner": "Michael Maconachie",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.10a Infrastructure Ready",
            "Category": "Schedule",
            "Inherent_Likelihood": 5,
            "Inherent_Consequence": 2,
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
            "Open_Days": 30,
            "Days_Since_Update": 5,
            "Stale_SLA": False,
            "Aging_Outlier": False,
            "Target_Date": "2026-07-31",
            "Target_Status": "Closed",
            "Critical_Update_7d": None,
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
            "Trend": "Worse ↓",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_5,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Open_Days": 27,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Target_Date": "2026-08-10",
            "Action_Plan": "Validating schedule impacts with CD1 Gap Closure Plan."
        },
        {
            "ID": "I-0004",
            "Name": "Delayed build of E01 due to product build quality issues",
            "Owner": "Scott Deacon",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "1.10b Platform Ready",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Trend": "Worse ↓",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_3,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Open_Days": 5,
            "Days_Since_Update": 1,
            "Stale_SLA": False,
            "Target_Date": "2026-08-12",
            "Action_Plan": "Drive escalation with Product team to enable E01."
        },
        {
            "ID": "I-0006",
            "Name": "GCP Environment O sandbox access delay for ACN",
            "Owner": "Scott Deacon",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Category": "Schedule",
            "Severity_Rating": "High",
            "Trend": "Better ↑",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": False,
            "Date_Raised": d_minus_10,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Open_Days": 10,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Target_Date": "2026-08-15",
            "Action_Plan": "Platform with ACN now; access provided."
        },
        {
            "ID": "I-0007",
            "Name": "DevSecOps (O) Core readiness delay",
            "Owner": "Tom Trobe",
            "RACI": "Responsible",
            "Driver_Tree_Ref": "1.7a DevSecOps",
            "Category": "Schedule",
            "Severity_Rating": "Critical",
            "Trend": "Same ↔",
            "Status": "Active",
            "Escalation_Status": "Internal",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_5,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Open_Days": 5,
            "Days_Since_Update": 3,
            "Stale_SLA": False,
            "Target_Date": "2026-08-20",
            "Action_Plan": "Platform validated; environment build commenced."
        },
        {
            "ID": "I-0011",
            "Name": "Lack of dedicated Export Control Officer resource",
            "Owner": "Mick Devine",
            "RACI": "Accountable",
            "Driver_Tree_Ref": "Export Compliance",
            "Category": "Scope",
            "Severity_Rating": "Critical",
            "Trend": "Worse ↓",
            "Status": "Active",
            "Escalation_Status": "IPF/PSG",
            "Escalation_Changed_7d": True,
            "Date_Raised": d_minus_3,
            "Date_Closed": None,
            "Last_Updated": d_minus_3,
            "Open_Days": 3,
            "Days_Since_Update": 1,
            "Stale_SLA": False,
            "Target_Date": "2026-08-15",
            "Action_Plan": "Recruitment in progress for dedicated EC Officer."
        }
    ]

    driver_tree_meta = {
        "1.10a Infrastructure Ready": {
            "title": "1.10a Infrastructure Ready",
            "owner": "Tom Trobe",
            "status": "Green 🟢 - Hardware delivery completed. E.01 initial infrastructure provisioning ready.",
            "last_updated": d_minus_3
        },
        "1.10b Platform Ready": {
            "title": "1.10b Platform Ready (GDC Enterprise E.01)",
            "owner": "Tom Trobe / Scott Deacon",
            "status": "Red 🔴 - Critical build quality and config delays impacting E01 platform readiness.",
            "last_updated": d_minus_3
        },
        "1.7a DevSecOps": {
            "title": "1.7a DevSecOps Core (GCP O & Tenancy)",
            "owner": "Scott Deacon / Tom Trobe",
            "status": "Amber 🟡 - GCP O sandbox access resolved for ACN; platform build underway.",
            "last_updated": d_minus_3
        },
        "Schedule 5 Governance": {
            "title": "Schedule 5 Governance & Contractual Provisions",
            "owner": "Susan Allin / Michael Maconachie",
            "status": "Amber 🟡 - Onerous reporting provisions under active legal review.",
            "last_updated": d_minus_3
        },
        "Export Compliance": {
            "title": "Export Controls & ITAR Governance",
            "owner": "Mick Devine",
            "status": "Red 🔴 - Dedicated Google Export Control Officer recruitment in progress.",
            "last_updated": d_minus_3
        }
    }

    return historical_df, pd.DataFrame(risks), pd.DataFrame(issues), driver_tree_meta

historical_df, df_risks, df_issues, driver_tree_meta = get_mock_data()
active_risks = df_risks[df_risks["Status"] == "Active"]
active_issues = df_issues[df_issues["Status"] == "Active"]

# -----------------------------------------------------------------------------
# RENDER VERSION 1: BASELINE CUSTOMER MOCKUP
# -----------------------------------------------------------------------------
def render_v1():
    st.sidebar.markdown("### 🛡️ Program filters")
    category_filter = st.sidebar.multiselect("Categories", ["Cost", "Scope", "Schedule", "Other"], default=["Cost", "Scope", "Schedule", "Other"], help="Filter dashboard metrics by normalized category.")
    owner_filter = st.sidebar.multiselect("Owners", sorted(list(set(active_risks["Owner"]).union(set(active_issues["Owner"])))), default=[], help="Filter items by Risk/Issue Owner.")

    filtered_risks = active_risks[active_risks["Category"].isin(category_filter)]
    filtered_issues = active_issues[active_issues["Category"].isin(category_filter)]
    if owner_filter:
        filtered_risks = filtered_risks[filtered_risks["Owner"].isin(owner_filter)]
        filtered_issues = filtered_issues[filtered_issues["Owner"].isin(owner_filter)]

    h_title_col, h_help_col = st.columns([4, 1])
    with h_title_col:
        st.title("📊 Project dashboard: Overall position (v1)")
        st.caption("Baseline customer specification mockup • Path: `?version=v1`")
    with h_help_col:
        st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)
        with st.popover("❓ Help & guide"):
            st.markdown("""
**Baseline Dashboard Guide (v1):**
- **Active risks & open issues:** Total count of active items. Deltas show net changes in the last 7 days.
- **5x5 Heatmap:** Risk density across Likelihood (1-Rare to 5-Almost Certain) vs. Consequence (1-Minor to 5-Critical).
- **Trend indicators:** `Better ↑` (risk reducing), `Worse ↓` (severity worsening), `Same ↔` (unchanged).
- **Driver tree:** Hierarchical milestone breakdown. Selecting a node filters risks/issues assigned to that driver tree item.
""")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active risks", len(filtered_risks), delta="-1 (Closed 7d)", delta_color="normal", help="Total active risks count.")
    with col2:
        st.metric("Open issues", len(filtered_issues), delta="+2 (New 7d)", delta_color="inverse", help="Total open issues count.")
    with col3:
        critical_count = len(filtered_risks[filtered_risks["Residual_Rating"] == "High"]) + len(filtered_issues[filtered_issues["Severity_Rating"] == "Critical"])
        st.metric("Critical items", critical_count, delta="0 (Net change)", delta_color="off", help="Combined count of High/Critical risks and issues.")
    with col4:
        st.metric("Overall trajectory", "Better ↑", delta="Stable convergence", delta_color="normal", help="Overall program risk trajectory.")

    st.markdown("<div style='margin-top: 0.4rem;'></div>", unsafe_allow_html=True)

    r1_col1, r1_col2 = st.columns([1.2, 1])
    with r1_col1:
        with st.container(border=True):
            st.markdown("### 🔥 5x5 Risk matrix heatmap")
            matrix_mode = st.radio("Rating view:", ["Residual Risk", "Inherent Risk"], horizontal=True, label_visibility="collapsed")
            like_col = "Residual_Likelihood" if matrix_mode == "Residual Risk" else "Inherent_Likelihood"
            cons_col = "Residual_Consequence" if matrix_mode == "Residual Risk" else "Inherent_Consequence"
            
            grid = pd.DataFrame(0, index=[5, 4, 3, 2, 1], columns=[1, 2, 3, 4, 5])
            for _, row in filtered_risks.iterrows():
                l, c = row[like_col], row[cons_col]
                if l in grid.index and c in grid.columns:
                    grid.loc[l, c] += 1
                    
            fig_heat = px.imshow(
                grid,
                labels=dict(x="Consequence (1-Minor → 5-Critical)", y="Likelihood (1-Rare → 5-Almost Certain)", color="Count"),
                x=["1-Minor", "2-Mod", "3-Signif", "4-Major", "5-Crit"],
                y=["5-Almost Certain", "4-Probable", "3-Occasional", "2-Improbable", "1-Rare"],
                color_continuous_scale=["#fce8e6", "#f28b82", "#d93025"],
                text_auto=True,
                aspect="auto"
            )
            fig_heat.update_layout(height=250, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_heat, use_container_width=True)

    with r1_col2:
        with st.container(border=True):
            st.markdown("### 📊 Distribution by category")
            r_cat = filtered_risks["Category"].value_counts().rename("Active risks")
            i_cat = filtered_issues["Category"].value_counts().rename("Open issues")
            df_cat = pd.concat([r_cat, i_cat], axis=1).fillna(0).reset_index()
            df_cat.columns = ["Category", "Active risks", "Open issues"]
            
            fig_bar = px.bar(
                df_cat,
                x="Category",
                y=["Active risks", "Open issues"],
                barmode="group",
                color_discrete_sequence=["#ea4335", "#fbbc04"],
                labels={"value": "Count", "variable": "Type"}
            )
            fig_bar.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_bar, use_container_width=True)

    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        with st.container(border=True):
            st.markdown("### 🔥 Top critical risks")
            top_5_risks = filtered_risks.sort_values(by=["Residual_Consequence", "Residual_Likelihood"], ascending=[False, False]).head(5)
            st.dataframe(top_5_risks[["ID", "Name", "Owner", "Category", "Residual_Rating", "Trend"]], use_container_width=True, hide_index=True, height=200)

    with r2_col2:
        with st.container(border=True):
            st.markdown("### 🚨 Top critical issues")
            severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
            filtered_issues_sorted = filtered_issues.copy()
            filtered_issues_sorted["Sev_Rank"] = filtered_issues_sorted["Severity_Rating"].map(severity_order)
            top_5_issues = filtered_issues_sorted.sort_values(by="Sev_Rank", ascending=False).head(5)
            st.dataframe(top_5_issues[["ID", "Name", "Owner", "Category", "Severity_Rating", "Trend"]], use_container_width=True, hide_index=True, height=200)

    with st.container(border=True):
        tab_act, tab_tree = st.tabs(["📅 7-day activity & escalations", "🌲 Interactive driver tree explorer"])
        with tab_act:
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                st.markdown("##### 🆕 Raised last 7 days")
                new_r = df_risks[df_risks["Date_Raised"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
                new_i = df_issues[df_issues["Date_Raised"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
                st.dataframe(pd.concat([new_r[["ID", "Name", "Category"]].assign(Type="Risk"), new_i[["ID", "Name", "Category"]].assign(Type="Issue")]), use_container_width=True, hide_index=True, height=140)
            with act_col2:
                st.markdown("##### 📢 Critical updates (7d)")
                st.dataframe(df_risks[df_risks["Critical_Update_7d"].notna()][["ID", "Owner", "Critical_Update_7d"]], use_container_width=True, hide_index=True, height=140)
            with act_col3:
                st.markdown("##### 🚀 Escalations (Internal & IPF/PSG)")
                st.dataframe(pd.concat([df_risks[df_risks["Escalation_Changed_7d"] == True][["ID", "Owner", "Escalation_Status"]].assign(Type="Risk"), df_issues[df_issues["Escalation_Changed_7d"] == True][["ID", "Owner", "Escalation_Status"]].assign(Type="Issue")]), use_container_width=True, hide_index=True, height=140)

        with tab_tree:
            dt_select_col, dt_info_col = st.columns([1, 2])
            with dt_select_col:
                driver_options = ["All / Program Overview"] + list(driver_tree_meta.keys())
                selected_node = st.selectbox("Select driver tree section:", driver_options, index=0)
            with dt_info_col:
                if selected_node != "All / Program Overview":
                    meta = driver_tree_meta[selected_node]
                    st.markdown(f"**{meta['title']}** • *Owner: {meta['owner']}*")
                    st.info(f"**Latest status update:** {meta['status']}")
                else:
                    st.caption("Select a section above to view status update.")
                    
            tree_r = filtered_risks if selected_node == "All / Program Overview" else filtered_risks[filtered_risks["Driver_Tree_Ref"] == selected_node]
            tree_i = filtered_issues if selected_node == "All / Program Overview" else filtered_issues[filtered_issues["Driver_Tree_Ref"] == selected_node]
            
            t_r_col, t_i_col = st.columns(2)
            with t_r_col:
                st.markdown(f"**Assigned risks ({len(tree_r)})**")
                st.dataframe(tree_r[["ID", "Name", "Category", "Residual_Rating", "Owner"]], use_container_width=True, hide_index=True, height=150)
            with t_i_col:
                st.markdown(f"**Assigned issues ({len(tree_i)})**")
                st.dataframe(tree_i[["ID", "Name", "Category", "Severity_Rating", "Owner"]], use_container_width=True, hide_index=True, height=150)

# -----------------------------------------------------------------------------
# RENDER VERSION 2: FULL UNIFIED DASHBOARD (V1 BASELINE + V2 ADVANCED FEATURES)
# -----------------------------------------------------------------------------
def render_v2():
    st.sidebar.markdown("### 🛡️ Program filters")
    category_filter = st.sidebar.multiselect("Categories", ["Cost", "Scope", "Schedule", "Other"], default=["Cost", "Scope", "Schedule", "Other"], key="v2_cat", help="Filter dashboard metrics by normalized category.")
    owner_filter = st.sidebar.multiselect("Owners", sorted(list(set(active_risks["Owner"]).union(set(active_issues["Owner"])))), default=[], key="v2_own", help="Filter items by Risk/Issue Owner.")

    filtered_risks = active_risks[active_risks["Category"].isin(category_filter)]
    filtered_issues = active_issues[active_issues["Category"].isin(category_filter)]
    if owner_filter:
        filtered_risks = filtered_risks[filtered_risks["Owner"].isin(owner_filter)]
        filtered_issues = filtered_issues[filtered_issues["Owner"].isin(owner_filter)]

    h_title_col, h_help_col = st.columns([4, 1])
    with h_title_col:
        st.title("📊 Project dashboard: Unified executive view (v2)")
        st.caption("Full Unified Dashboard (v1 Customer Baseline + v2 Advanced Governance) • Path: `?version=v2`")
    with h_help_col:
        st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)
        with st.popover("❓ Help & guide"):
            st.markdown("""
**v2 Unified Dashboard Guide:**
- Includes all **v1 Baseline Features** (5x5 Heatmap, Top 5 Tables, 7-Day Deltas, Driver Tree Explorer).
- Plus all **v2 Advanced Features** (AI Weekly Summary Generator, SLA & Aging Radar, RACI Workload Matrix, 12-Week Burn-Down, Sankey Dependency Graph, 1-Click Deck Export).
""")

    # 1. KPI Metric Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active risks", len(filtered_risks), delta="-1 (Closed 7d)", delta_color="normal", help="Total active risks count.")
    with col2:
        st.metric("Open issues", len(filtered_issues), delta="+2 (New 7d)", delta_color="inverse", help="Total open issues count.")
    with col3:
        critical_count = len(filtered_risks[filtered_risks["Residual_Rating"] == "High"]) + len(filtered_issues[filtered_issues["Severity_Rating"] == "Critical"])
        st.metric("Critical items", critical_count, delta="0 (Net change)", delta_color="off", help="Combined count of High/Critical risks and issues.")
    with col4:
        st.metric("Overall trajectory", "Better ↑", delta="Stable convergence", delta_color="normal", help="Overall program risk trajectory.")

    st.markdown("<div style='margin-top: 0.4rem;'></div>", unsafe_allow_html=True)

    # 2. AI Executive Weekly Briefing Accordion / Box (v2 Feature)
    with st.expander("🤖 **AI-Assisted Weekly Executive Summary (Week Ending 04 Aug 2026)**", expanded=False):
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
        b_col1, b_col2 = st.columns([1, 4])
        with b_col1:
            if st.button("📋 Copy summary", key="v2_copy"): st.toast("Copied!", icon="✅")
        with b_col2:
            st.download_button("📥 Download (.md)", summary_md, "FDSE_Executive_Summary.md", "text/markdown", key="v2_dl")

    # 3. Row 1: 5x5 Heatmap & Category Distribution (v1 Baseline Feature)
    r1_col1, r1_col2 = st.columns([1.2, 1])
    with r1_col1:
        with st.container(border=True):
            st.markdown("### 🔥 5x5 Risk matrix heatmap")
            matrix_mode = st.radio("Rating view:", ["Residual Risk", "Inherent Risk"], horizontal=True, label_visibility="collapsed", key="v2_mat")
            like_col = "Residual_Likelihood" if matrix_mode == "Residual Risk" else "Inherent_Likelihood"
            cons_col = "Residual_Consequence" if matrix_mode == "Residual Risk" else "Inherent_Consequence"
            
            grid = pd.DataFrame(0, index=[5, 4, 3, 2, 1], columns=[1, 2, 3, 4, 5])
            for _, row in filtered_risks.iterrows():
                l, c = row[like_col], row[cons_col]
                if l in grid.index and c in grid.columns:
                    grid.loc[l, c] += 1
                    
            fig_heat = px.imshow(
                grid,
                labels=dict(x="Consequence (1-Minor → 5-Critical)", y="Likelihood (1-Rare → 5-Almost Certain)", color="Count"),
                x=["1-Minor", "2-Mod", "3-Signif", "4-Major", "5-Crit"],
                y=["5-Almost Certain", "4-Probable", "3-Occasional", "2-Improbable", "1-Rare"],
                color_continuous_scale=["#fce8e6", "#f28b82", "#d93025"],
                text_auto=True,
                aspect="auto"
            )
            fig_heat.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_heat, use_container_width=True)

    with r1_col2:
        with st.container(border=True):
            st.markdown("### 📊 Distribution by category")
            r_cat = filtered_risks["Category"].value_counts().rename("Active risks")
            i_cat = filtered_issues["Category"].value_counts().rename("Open issues")
            df_cat = pd.concat([r_cat, i_cat], axis=1).fillna(0).reset_index()
            df_cat.columns = ["Category", "Active risks", "Open issues"]
            
            fig_bar = px.bar(
                df_cat,
                x="Category",
                y=["Active risks", "Open issues"],
                barmode="group",
                color_discrete_sequence=["#ea4335", "#fbbc04"],
                labels={"value": "Count", "variable": "Type"}
            )
            fig_bar.update_layout(height=265, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_bar, use_container_width=True)

    # 4. Row 2: Top 5 Critical Risks & Top 5 Critical Issues (v1 Baseline Feature)
    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        with st.container(border=True):
            st.markdown("### 🔥 Top critical risks")
            top_5_risks = filtered_risks.sort_values(by=["Residual_Consequence", "Residual_Likelihood"], ascending=[False, False]).head(5)
            st.dataframe(top_5_risks[["ID", "Name", "Owner", "Category", "Residual_Rating", "Trend"]], use_container_width=True, hide_index=True, height=190)

    with r2_col2:
        with st.container(border=True):
            st.markdown("### 🚨 Top critical issues")
            severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
            filtered_issues_sorted = filtered_issues.copy()
            filtered_issues_sorted["Sev_Rank"] = filtered_issues_sorted["Severity_Rating"].map(severity_order)
            top_5_issues = filtered_issues_sorted.sort_values(by="Sev_Rank", ascending=False).head(5)
            st.dataframe(top_5_issues[["ID", "Name", "Owner", "Category", "Severity_Rating", "Trend"]], use_container_width=True, hide_index=True, height=190)

    # 5. Row 3: Advanced Governance & Analytics (v2 SLA Radar & RACI Workload)
    r3_col1, r3_col2 = st.columns(2)
    with r3_col1:
        with st.container(border=True):
            st.markdown("### ⏰ Stale SLA radar (>14d update SLA)")
            stale_risks = filtered_risks[filtered_risks["Stale_SLA"] == True]
            if len(stale_risks) > 0:
                st.dataframe(stale_risks[["ID", "Name", "Owner", "Days_Since_Update", "Target_Status"]], use_container_width=True, hide_index=True, height=180)
            else:
                st.success("All active items compliant with 14-day update SLA!")

    with r3_col2:
        with st.container(border=True):
            st.markdown("### 👤 Owner RACI workload distribution")
            combined_owners = pd.concat([
                filtered_risks[["ID", "Name", "Owner", "RACI", "Residual_Rating"]].rename(columns={"Residual_Rating": "Rating"}),
                filtered_issues[["ID", "Name", "Owner", "RACI", "Severity_Rating"]].rename(columns={"Severity_Rating": "Rating"})
            ])
            fig_raci = px.bar(combined_owners, x="Owner", color="Rating", barmode="stack", color_discrete_map={"Critical": "#D32F2F", "High": "#F57C00", "Medium": "#FBC02D", "Low": "#388E3C"})
            fig_raci.update_layout(height=180, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_raci, use_container_width=True)

    # 6. Row 4: 12-Week Trendline & Sankey Blocker Graph (v2 Advanced Features)
    r4_col1, r4_col2 = st.columns(2)
    with r4_col1:
        with st.container(border=True):
            st.markdown("### 📈 12-Week historical burn-down")
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=historical_df["Week"], y=historical_df["Active Risks"], mode="lines+markers", name="Active Risks", line=dict(color="#E53935", width=2)))
            fig_trend.add_trace(go.Scatter(x=historical_df["Week"], y=historical_df["Closed Risks (Cumulative)"], mode="lines+markers", name="Closed Risks", line=dict(color="#43A047", width=2, dash="dash")))
            fig_trend.add_trace(go.Scatter(x=historical_df["Week"], y=historical_df["Open Issues"], mode="lines+markers", name="Open Issues", line=dict(color="#FB8C00", width=2)))
            fig_trend.update_layout(height=230, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_trend, use_container_width=True)

    with r4_col2:
        with st.container(border=True):
            st.markdown("### 🔗 Driver tree blocker dependency graph")
            nodes = ["Issue I-0004", "Issue I-0003", "Risk R-0001", "Risk R-0002", "1.10b Platform", "1.10c Env Ready", "1.10d Mission", "1.13 IBR"]
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(pad=10, thickness=15, label=nodes, color=["#E53935", "#E53935", "#FB8C00", "#FB8C00", "#1E88E5", "#1E88E5", "#1E88E5", "#43A047"]),
                link=dict(source=[0, 1, 2, 3], target=[6, 5, 7, 5], value=[1, 1, 1, 1])
            )])
            fig_sankey.update_layout(height=230, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_sankey, use_container_width=True)

    # 7. Row 5: 7-Day Activity & Driver Tree Explorer Tabs + Deck Export (v1 + v2 Unified)
    with st.container(border=True):
        tab_act, tab_tree, tab_export = st.tabs(["📅 7-day activity & escalations", "🌲 Interactive driver tree explorer", "📄 1-click executive deck export"])
        
        with tab_act:
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                st.markdown("##### 🆕 Raised last 7 days")
                new_r = df_risks[df_risks["Date_Raised"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
                new_i = df_issues[df_issues["Date_Raised"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
                st.dataframe(pd.concat([new_r[["ID", "Name", "Category"]].assign(Type="Risk"), new_i[["ID", "Name", "Category"]].assign(Type="Issue")]), use_container_width=True, hide_index=True, height=140)
            with act_col2:
                st.markdown("##### 📢 Critical updates (7d)")
                st.dataframe(df_risks[df_risks["Critical_Update_7d"].notna()][["ID", "Owner", "Critical_Update_7d"]], use_container_width=True, hide_index=True, height=140)
            with act_col3:
                st.markdown("##### 🚀 Escalations (Internal & IPF/PSG)")
                st.dataframe(pd.concat([df_risks[df_risks["Escalation_Changed_7d"] == True][["ID", "Owner", "Escalation_Status"]].assign(Type="Risk"), df_issues[df_issues["Escalation_Changed_7d"] == True][["ID", "Owner", "Escalation_Status"]].assign(Type="Issue")]), use_container_width=True, hide_index=True, height=140)

        with tab_tree:
            dt_select_col, dt_info_col = st.columns([1, 2])
            with dt_select_col:
                driver_options = ["All / Program Overview"] + list(driver_tree_meta.keys())
                selected_node = st.selectbox("Select driver tree section:", driver_options, index=0, key="v2_dt_sel")
            with dt_info_col:
                if selected_node != "All / Program Overview":
                    meta = driver_tree_meta[selected_node]
                    st.markdown(f"**{meta['title']}** • *Owner: {meta['owner']}*")
                    st.info(f"**Latest status update:** {meta['status']}")
                else:
                    st.caption("Select a section above to view status update.")
                    
            tree_r = filtered_risks if selected_node == "All / Program Overview" else filtered_risks[filtered_risks["Driver_Tree_Ref"] == selected_node]
            tree_i = filtered_issues if selected_node == "All / Program Overview" else filtered_issues[filtered_issues["Driver_Tree_Ref"] == selected_node]
            
            t_r_col, t_i_col = st.columns(2)
            with t_r_col:
                st.markdown(f"**Assigned risks ({len(tree_r)})**")
                st.dataframe(tree_r[["ID", "Name", "Category", "Residual_Rating", "Owner"]], use_container_width=True, hide_index=True, height=150)
            with t_i_col:
                st.markdown(f"**Assigned issues ({len(tree_i)})**")
                st.dataframe(tree_i[["ID", "Name", "Category", "Severity_Rating", "Owner"]], use_container_width=True, hide_index=True, height=150)

        with tab_export:
            st.markdown("##### Export Executive Snapshot")
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                st.download_button("📥 Export Executive PDF Deck (.pdf)", "PDF Mock Content", "FDSE_Executive_Deck.pdf", "application/pdf", key="v2_pdf")
            with e_col2:
                st.download_button("📊 Export Slide Deck (.pptx)", "PPTX Mock Content", "FDSE_Executive_Deck.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", key="v2_pptx")

# -----------------------------------------------------------------------------
# MAIN DISPATCHER
# -----------------------------------------------------------------------------
if current_v == "v1":
    render_v1()
else:
    render_v2()

st.markdown("---")
st.caption(f"F-DSE Project Dashboard • Currently viewing **{current_v.upper()}** • Streamlit Port 9000")
