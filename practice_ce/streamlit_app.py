import streamlit as st
import pandas as pd
from data_store import DataStore

st.set_page_config(page_title="CEBank International Compliance System UI", layout="wide")

st.title("🏦 CEBank International - Compliance Data Viewer")
st.markdown("This dashboard provides a direct view into the mock database to assist with verifying the SOAP interface connector logic. It bypasses the SOAP interface completely to show the ground truth.")

# Load the database
try:
    db = DataStore()
except FileNotFoundError:
    st.error("Mock database not found. Please ensure `generate_mock_data.py` has been run.")
    st.stop()

# --- Users Viewer ---
st.header("👥 System Users")
st.markdown("These are the simulated users that can authenticate via SOAP Header/Basic Auth for your connector demo.")
users_df = pd.DataFrame(db.data.get("users", []))
# Mask passwords for display
if not users_df.empty:
    display_users_df = users_df.copy()
    display_users_df["password"] = "********"
    st.dataframe(display_users_df, use_container_width=True)

st.divider()

# --- Compliance Documents & Logs ---
tab1, tab2, tab3 = st.tabs(["📜 Trading Rules", "📁 Regulatory Filings", "🔍 Audit Logs"])

with tab1:
    st.subheader("Trading Rules")
    st.markdown("Organizational rules governing expected trader behavior.")
    rules = db.data.get("trading_rules", [])
    if rules:
        df = pd.DataFrame(rules)
        # Convert list of ACLs to string for better display
        df['acl'] = df['acl'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No trading rules found.")

with tab2:
    st.subheader("Regulatory Filings")
    st.markdown("Internal and external reports. Note the restricted Access Control Lists (ACLs).")
    filings = db.data.get("regulatory_filings", [])
    if filings:
        df = pd.DataFrame(filings)
        df['acl'] = df['acl'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No regulatory filings found.")

with tab3:
    st.subheader("Audit Logs")
    st.markdown("System logs for all user activity. Critical for demonstrating investigative search workflows.")
    
    # Optional filtering
    search_term = st.text_input("Filter details or action:", "")
    
    logs = db.data.get("audit_logs", [])
    if logs:
        df = pd.DataFrame(logs)
        df['acl'] = df['acl'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
        if search_term:
            # Case insensitive search on action or details
            mask = df['action'].str.contains(search_term, case=False, na=False) | df['details'].str.contains(search_term, case=False, na=False)
            df = df[mask]
            
        st.dataframe(df, use_container_width=True, height=600)
    else:
        st.info("No audit logs found.")

st.caption("Powered by Streamlit & Spyne SOAP Mock")
