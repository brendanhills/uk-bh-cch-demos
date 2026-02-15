import streamlit as st
import pandas as pd
from data_store import DataStore
from google.cloud import discoveryengine
from google.api_core.client_options import ClientOptions
import connector_app.config as config
import sys
import subprocess
import socket
import time
import os

# Page Config
st.set_page_config(page_title="CEBank Compliance Portal", layout="wide", initial_sidebar_state="expanded")

# --- STRICT PORT CHECK ---
# Ensure the app is running on port 8501 for Deep Linking to work.
try:
    # Use 'ss' to check if our process is listening on port 8501
    # We grep for our PID in the listening sockets list
    cmd = f"ss -lptn | grep pid={os.getpid()}"
    process_ports = subprocess.check_output(cmd, shell=True).decode()
    
    if ":8501" not in process_ports:
        st.error("🚨 CRITICAL ERROR: Application is NOT running on Port 8501!")
        st.markdown(
            """
            **Why this matters:** The search index contains hardcoded links to `localhost:8501`. 
            If the app runs on a different port (e.g. 8502), deep links from the search results will fail.
            """
        )
        st.warning("Please kill the process blocking 8501 and restart:")
        st.code("fuser -k 8501/tcp\nstreamlit run compliance_app.py", language="bash")
        st.stop()
except Exception:
    # specific 'ss' command might fail on some environments (e.g. no permissions), 
    # but we proceed if we can't verify.
    pass

# Disable "Fade" Transitions
st.markdown(
    """
    <style>
        .stAppViewContainer {
            transition: none !important;
            animation: none !important;
        }
        .element-container {
            transition: none !important;
            animation: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.title("CEBank Compliance")

# Load the database (Global for all pages that need it)
try:
    db = DataStore()
except FileNotFoundError:
    st.error("System Error: Database not initialized. Run `generate_mock_data.py`.")
    st.stop()

# User Simulation Context
st.sidebar.subheader("Simulated Context")

# Get real admin user
try:
    admin_email = subprocess.check_output(
        ["gcloud", "config", "get-value", "account"], 
        text=True
    ).strip()
except Exception:
    admin_email = "admin@example.com"

# Create sorted user list (Admin first)
db_users = [u['username'] for u in db.data.get("users", [])]
other_users = sorted([u for u in db_users if u != admin_email])
available_users = [admin_email] + other_users

# Helper to reset
def reset_to_admin():
    st.session_state.selected_user = admin_email

# User Selection with Session State
if "selected_user" not in st.session_state:
    st.session_state.selected_user = available_users[0]

# Ensure the session state value is valid (e.g. if list changed)
if st.session_state.selected_user not in available_users:
    st.session_state.selected_user = available_users[0]

current_username = st.sidebar.selectbox("Current User:", available_users, key="selected_user")

if current_username != admin_email:
    st.sidebar.button("Reset to Admin", on_click=reset_to_admin)

if current_username == admin_email:
    current_user_role = "System Admin"
else:
    current_user_role = db.get_user_role(current_username)

st.sidebar.caption(f"Role: {current_user_role}")
st.sidebar.divider()

# Permission Logic
available_modules = ["Compliance Data Registry", "Identity Management"]
if current_user_role in ["Compliance", "Connector", "Executive", "Auditor", "System Admin"]:
    available_modules.append("Audit Logs")
    available_modules.append("System Administration")

page = st.sidebar.radio("Module:", available_modules)


# --- PAGE 1: Identity Management ---
if page == "Identity Management":
    st.title("Identity & Access Management")
    st.markdown("Centralized registry of authorized personnel and security roles.")

    # Load Policy Data
    acls_data = db.data.get("acls", {})
    roles_policy = acls_data.get("roles", {})
    sensitivity_levels = acls_data.get("sensitivity_levels", {})

    # Create Tabs for Different Views
    tab_users, tab_policies, tab_matrix = st.tabs(["👤 User Directory", "📜 Role Policies", "🛡️ Access Matrix"])

    with tab_users:
        st.subheader("Authorized Personnel")
        users_df = pd.DataFrame(db.data.get("users", []))
        
        if not users_df.empty:
            display_users_df = users_df.copy()
            display_users_df = display_users_df.rename(columns={"username": "User ID", "role": "Security Role"})
            display_users_df["password"] = "********"
            
            # Interactive Selection
            event = st.dataframe(
                display_users_df, 
                width="stretch",
                on_select="rerun",
                selection_mode="single-row",
                hide_index=True
            )
            
            if len(event.selection.rows) > 0:
                selected_index = event.selection.rows[0]
                selected_user = users_df.iloc[selected_index]
                user_role = selected_user['role']
                
                st.divider()
                st.subheader(f"User Profile: {selected_user['username']}")
                cols = st.columns(3)
                cols[0].info(f"**Role**: {user_role}")
                cols[1].success("**Status**: Active")
                cols[2].caption(f"Identity Source: CEBank LDAP")

                # Show Permissions
                st.markdown("#### 🔑 Effective Permissions")
                if user_role in roles_policy:
                    perms = roles_policy[user_role].get("permissions", [])
                    if perms:
                        perm_df = pd.DataFrame(perms)
                        perm_df = perm_df.rename(columns={"category": "Document Category", "max_sensitivity": "Max Allowed Sensitivity"})
                        st.table(perm_df)
                    else:
                        st.warning("No explicit permissions defined for this role.")
                elif user_role in ["System Admin", "Connector"]:
                    st.success("✅ **Full System Access** (Superuser)")
                else:
                    st.error("❌ Role not defined in Security Policy.")

                # Show Accessible Documents Count
                st.markdown("#### 📊 Accessible Data Volume")
                
                # Filter Rules
                rules = db.data.get("trading_rules", [])
                acc_rules = sum(1 for r in rules if db.is_authorized(r, selected_user['username'], user_role))
                
                # Filter Filings
                filings = db.data.get("regulatory_filings", [])
                acc_filings = sum(1 for f in filings if db.is_authorized(f, selected_user['username'], user_role))
                
                # Filter Logs (Own logs always specific, generic count tricky without context)
                # Just show count of ALL logs they can see (permission based)
                logs = db.data.get("audit_logs", [])
                acc_logs = sum(1 for l in logs if db.is_authorized(l, selected_user['username'], user_role))

                m1, m2, m3 = st.columns(3)
                m1.metric("Trading Rules", acc_rules)
                m2.metric("Reg Filings", acc_filings)
                m3.metric("Audit Logs", acc_logs)

        else:
            st.info("No users found in directory.")

    with tab_policies:
        st.subheader("Role Policy Definitions")
        st.markdown("Detailed breakdown of permissions assigned to each role.")
        
        for role_name, policy in roles_policy.items():
            with st.expander(f"Role: {role_name}", expanded=False):
                perms = policy.get("permissions", [])
                if perms:
                    st.table(pd.DataFrame(perms).rename(columns={"category": "Category", "max_sensitivity": "Max Sensitivity"}))
                else:
                    st.info("No specific permissions.")

    with tab_matrix:
        st.subheader("Global Access Control Matrix")
        st.markdown("Overview of access levels by Role and Category.")
        
        # Build a Matrix: Rows = Roles, Cols = Categories, Val = Max Sensitivity
        
        # Get all unique categories from policy
        all_cats = set()
        for p in roles_policy.values():
            for perm in p.get("permissions", []):
                all_cats.add(perm["category"])
        
        matrix_data = []
        for role_name, policy in roles_policy.items():
            row = {"Role": role_name}
            for cat in all_cats:
                # Find permission for this cat
                perm = next((p for p in policy.get("permissions", []) if p["category"] == cat), None)
                if perm:
                    row[cat] = perm["max_sensitivity"]
                else:
                    row[cat] = "🚫 None"
            matrix_data.append(row)
            
        if matrix_data:
            matrix_df = pd.DataFrame(matrix_data).set_index("Role")
            st.dataframe(matrix_df, width="stretch")
        else:
            st.info("No policy data available to build matrix.")
            
        st.caption("Legend: Public < Internal < Confidential < Restricted")


# --- PAGE 2: Compliance Data Registry ---
elif page == "Compliance Data Registry":
    st.title("Compliance Data Registry")
    st.markdown("Authorized access to the central compliance database. This view reflects the system of record.")

    st.divider()

    # --- Document Lookup (Access Denied Simulation) ---
    with st.expander("🔍 Document Lookup (Test Access Control)", expanded=False):
        st.info("Use this tool to test access control by looking up specific Document IDs (e.g., TR-001, TR-003).")
        # Use dynamic key to reset input when user changes
        lookup_id = st.text_input("Enter Document ID:", placeholder="e.g., TR-004 (Restricted)", key=f"lookup_{current_username}")
        
        if lookup_id:
            # Search ALL documents (ignoring permissions initially to find it)
            all_rules = db.data.get("trading_rules", [])
            all_filings = db.data.get("regulatory_filings", [])
            
            target_doc = next((d for d in all_rules if d["id"] == lookup_id), None)
            doc_type = "Trading Rule"
            
            if not target_doc:
                target_doc = next((d for d in all_filings if d["id"] == lookup_id), None)
                doc_type = "Regulatory Filing"
            
            if target_doc:
                # Check Authorization
                is_authorized = db.is_authorized(target_doc, current_username, current_user_role)
                
                # DEBUG: Trace permissions
                st.caption(f"[DEBUG] User: {current_username} | Role: {current_user_role} | Doc Sensitivity: {target_doc.get('sensitivity')} | Authorized: {is_authorized}")
                
                if is_authorized:
                    st.success(f"✅ Access Granted: {doc_type}")
                    st.markdown(f"**Title**: {target_doc['title']}")
                    st.markdown(f"**Sensitivity**: `{target_doc.get('sensitivity', 'Unknown')}`")
                    st.markdown("---")
                    st.write(target_doc.get('content', target_doc.get('summary', 'No content')))
                else:
                    st.error(f"🚫 Access Denied: {doc_type}")
                    st.markdown(f"**Document ID**: `{lookup_id}`")
                    st.markdown(f"**Sensitivity**: `{target_doc.get('sensitivity', 'Unknown')}`")
                    st.warning(f"User '{current_username}' (Role: {current_user_role}) does not have permission to view this document.")
                    
                    # Log the denied attempt
                    if st.session_state.get(f"log_deny_{lookup_id}") != True:
                        db.add_audit_log(
                            username=current_username,
                            action="ACCESS_DENIED",
                            details=f"Attempted to access {doc_type}: {lookup_id}",
                        )
                        st.session_state[f"log_deny_{lookup_id}"] = True
            else:
                st.warning(f"Document ID '{lookup_id}' not found.")

    st.divider()

    # --- Deep Link Handler ---
    query_params = st.query_params
    target_id = query_params.get("id")
    
    if target_id:
        # Try to find in Rules
        rules = db.get_trading_rules(current_username, current_user_role)
        target_rule = next((r for r in rules if r["id"] == target_id), None)
        
        if target_rule:
            if st.button("← Back to Registry"):
                st.query_params.clear()
                st.rerun()
                
            st.markdown(f"### 📄 {target_rule['title']}")
            st.info(f"**Rule ID**: {target_rule['id']} | **Sensitivity**: {target_rule.get('sensitivity', 'Restricted')}")
            st.markdown("#### Full Description")
            st.write(target_rule['content'])
            
            # Log View
            if st.session_state.get(f"log_deep_{target_rule['id']}") != True:
                db.add_audit_log(
                    username=current_username,
                    action="DOCUMENT_READ",
                    details=f"Viewed (Deep Link) Trading Rule: {target_rule['id']}",
                )
                st.session_state[f"log_deep_{target_rule['id']}"] = True

            st.stop() # Only show the deep linked item

        # Try to find in Filings
        filings = db.get_regulatory_filings(current_username, current_user_role)
        target_filing = next((f for f in filings if f["id"] == target_id), None)
        
        if target_filing:
            if st.button("← Back to Registry"):
                st.query_params.clear()
                st.rerun()

            st.markdown(f"### 📁 {target_filing['title']}")
            st.info(f"**Document ID**: {target_filing['id']} | **Regulator**: {target_filing['regulator']} | **Status**: {target_filing['status']}")
            st.markdown("#### Executive Summary")
            st.write(target_filing['summary'])
            
            # Log View
            if st.session_state.get(f"log_deep_{target_filing['id']}") != True:
                db.add_audit_log(
                    username=current_username,
                    action="DOCUMENT_READ",
                    details=f"Viewed (Deep Link) Regulatory Filing: {target_filing['id']}",
                )
                st.session_state[f"log_deep_{target_filing['id']}"] = True

            st.stop()
            
        st.warning(f"Document ID '{target_id}' not found or access denied.")
        if st.button("Clear Filter"):
            st.query_params.clear()
            st.rerun()

    # --- Compliance Documents ---
    tab1, tab2 = st.tabs(["Trading Standards", "Regulatory Filings"])

    with tab1:
        st.subheader("Trading Standards & Restrictions")
        rules = db.get_trading_rules(current_username, current_user_role)
        if rules:
            df = pd.DataFrame(rules)
            # PBAC: Show Sensitivity instead of ACL
            display_df = df.rename(columns={"id": "Rule ID", "title": "Regulation", "content": "Description", "sensitivity": "Sensitivity"})
            
            # Interactive Selection
            event = st.dataframe(
                display_df, 
                width="stretch",
                on_select="rerun",
                selection_mode="single-row",
                hide_index=True
            )
            
            if len(event.selection.rows) > 0:
                selected_index = event.selection.rows[0]
                selected_rule = df.iloc[selected_index]
                
                # Audit Logging
                if st.session_state.get(f"log_rule_{selected_rule['id']}") != True:
                    db.add_audit_log(
                        username=current_username,
                        action="DOCUMENT_READ",
                        details=f"Viewed Trading Rule: {selected_rule['id']} - {selected_rule['title']}",
                    )
                    st.session_state[f"log_rule_{selected_rule['id']}"] = True # Prevent duplicate logs on rerun
                
                st.divider()
                st.markdown(f"### 📄 {selected_rule['title']}")
                st.info(f"**Rule ID**: {selected_rule['id']} | **Sensitivity**: {selected_rule.get('sensitivity', 'Restricted')}")
                st.markdown("#### Full Description")
                st.write(selected_rule['content'])
                st.warning("⚠️ Application of this rule is mandatory for all identified personnel.")
        else:
            st.info("No records found (Access Denied).")

    with tab2:
        st.subheader("Regulatory Documentation")
        filings = db.get_regulatory_filings(current_username, current_user_role)
        if filings:
            df = pd.DataFrame(filings)
            display_df = df.rename(columns={"id": "Document ID", "title": "Filing Title", "summary": "Summary", "sensitivity": "Sensitivity"})
            
            # Interactive Selection
            event = st.dataframe(
                display_df, 
                width="stretch",
                on_select="rerun",
                selection_mode="single-row",
                hide_index=True
            )
            
            if len(event.selection.rows) > 0:
                selected_index = event.selection.rows[0]
                selected_filing = df.iloc[selected_index]
                
                # Audit Logging
                # Simple dedup: Only log if selection changed
                last_viewed = st.session_state.get("last_viewed_filing")
                if last_viewed != selected_filing['id']:
                     db.add_audit_log(
                        username=current_username,
                        action="DOCUMENT_READ",
                        details=f"Viewed Regulatory Filing: {selected_filing['id']} - {selected_filing['title']}",
                    )
                     st.session_state["last_viewed_filing"] = selected_filing['id']

                st.divider()
                st.markdown(f"### 📁 {selected_filing['title']}")
                st.info(f"**Document ID**: {selected_filing['id']} | **Regulator**: {selected_filing['regulator']} | **Status**: {selected_filing['status']}")
                st.markdown("#### Executive Summary")
                st.write(selected_filing['summary'])
                st.caption(f"Sensitivity: {selected_filing.get('sensitivity', 'Unknown')}")
                
        else:
            st.info("No records found (Access Denied).")

    st.caption("Confidential - For Internal Use Only - CEBank Compliance Division")

# --- PAGE 3: Audit Logs ---
elif page == "Audit Logs":
    st.title("System Audit Logs")
    st.markdown("Secure record of all access events and system activities.")
    st.divider()
    
    logs = db.get_audit_logs(current_username, current_user_role)
    # Sort by timestamp descending (newest first)
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    if logs:
        # Simple Search
        log_search = st.text_input("Filter Logs:", placeholder="User, Action, or Details...")
        
        df = pd.DataFrame(logs)
        # Fix for missing 'acl' - Audit logs still have category/sensitivity but maybe not useful to show
        display_logs = df.rename(columns={"id": "Log ID", "timestamp": "Time (UTC)", "action": "Event", "details": "Event Details", "userId": "Actor"})
        
        if log_search:
            mask = display_logs.apply(lambda x: x.astype(str).str.contains(log_search, case=False).any(), axis=1)
            display_logs = display_logs[mask]

        st.dataframe(
            display_logs, 
            width="stretch", 
            height=600,
            hide_index=True
        )
    else:
        st.info("No logs found.")


# --- PAGE 4: System Administration ---
elif page == "System Administration":
    st.title("System Administration Console")
    st.markdown("Vertex AI Search Connector Diagnostics & Control Plane.")

    project_id = config.PROJECT_ID
    location = config.LOCATION

    st.sidebar.divider()
    st.sidebar.info(f"Connected to: {project_id} ({location})")

    # --- SOAP Service Control ---
    def is_port_open(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('localhost', port)) == 0

    st.subheader("🔌 Connector Service Status")
    c1, c2 = st.columns([1, 3])
    
    soap_running = is_port_open(8000)
    
    with c1:
        if soap_running:
            st.success("Online (Port 8000)")
        else:
            st.error("Offline")
            
    with c2:
        if not soap_running:
            if st.button("Start SOAP Service"):
                try:
                    # Run in background
                    subprocess.Popen([sys.executable, "-m", "uvicorn", "compliance_soap_service:app", "--host", "0.0.0.0", "--port", "8000"])
                    st.toast("Service starting...", icon="🚀")
                    time.sleep(3)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to start: {e}")
        else:
            st.caption("Service is active and ready for connector requests.")

    st.divider()

    @st.cache_resource
    def get_clients():
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        ds_client = discoveryengine.DataStoreServiceClient(client_options=client_options)
        doc_client = discoveryengine.DocumentServiceClient(client_options=client_options)
        engine_client = discoveryengine.EngineServiceClient(client_options=client_options)
        return ds_client, doc_client, engine_client

    try:
        ds_client, doc_client, engine_client = get_clients()
        parent = ds_client.collection_path(project=project_id, location=location, collection="default_collection")
        
        # Build DataStore -> App Map and find target Data Stores
        app_map = {}
        target_ds_ids = set()
        
        try:
            # Engines are also collections of data stores
            engine_req = discoveryengine.ListEnginesRequest(parent=parent)
            engines = engine_client.list_engines(request=engine_req)
            for engine in engines:
                # Check if this is our configured engine
                is_target_engine = False
                if config.ENGINE_ID and (config.ENGINE_ID in engine.name):
                    is_target_engine = True
                
                for ds_id in engine.data_store_ids:
                    app_map[ds_id] = engine.display_name
                    if is_target_engine:
                        target_ds_ids.add(ds_id)
                        
        except Exception:
            pass # Ignore if no permissions or no engines

        # List all data stores
        request = discoveryengine.ListDataStoresRequest(parent=parent)
        page_result = ds_client.list_data_stores(request=request)
        
        data_stores = []
        for ds in page_result:
            ds_id = ds.name.split("/")[-1]
            
            # FILTER: Only show if it belongs to our configured Engine
            if target_ds_ids and ds_id not in target_ds_ids:
                continue
                
            data_stores.append({
                "Data Store ID": ds_id,
                "Display Name": ds.display_name,
                "Connected App": app_map.get(ds_id, "⚠️ Unattached"),
                "Solution Type": [t.name for t in ds.solution_types],
                "Vertical": ds.industry_vertical.name,
                "Created": ds.create_time,
                "Resource Name": ds.name
            })
            
        if not data_stores:
            st.warning(f"No Data Stores found for Engine ID: {config.ENGINE_ID}")
        else:
            df = pd.DataFrame(data_stores)

            st.subheader("Configured Data Stores")
            st.dataframe(df.drop(columns=["Resource Name"]), width="stretch")
            
            st.divider()
            st.subheader("Index Inspection")
            
            ds_options = [d["Data Store ID"] for d in data_stores]
            default_index = 0
            if config.DATA_STORE_ID in ds_options:
                default_index = ds_options.index(config.DATA_STORE_ID)
            
            selected_ds_id = st.selectbox("Select Target Data Store:", ds_options, index=default_index)
            
            if selected_ds_id:
                branch_path = doc_client.branch_path(
                    project=project_id,
                    location=location,
                    data_store=selected_ds_id,
                    branch="default_branch"
                )
                
                st.info("Click below to sample documents from the live index. (Rate Limited)")
                if st.button("Scan Index (Sample 5 Docs)"):
                    with st.spinner("Fetching documents..."):
                        try:
                            # List documents (just a few to verify)
                            list_req = discoveryengine.ListDocumentsRequest(parent=branch_path, page_size=5)
                            docs_page = doc_client.list_documents(request=list_req)
                            
                            docs = []
                            for doc in docs_page:
                                docs.append({
                                    "Document ID": doc.id,
                                    "Source URI": doc.content.uri if doc.content else doc.struct_data.get("uri", "N/A"),
                                    "Schema ID": doc.schema_id,
                                })
                                
                            if docs:
                                st.success(f"Index Active: {len(docs)} documents retrieved.")
                                st.table(docs)
                            else:
                                st.warning("Index Empty: No documents found.")
                                
                        except Exception as e:
                            if "Quota exceeded" in str(e):
                                st.error("API Quota Exceeded. Please wait a minute before scanning again.")
                            else:
                                st.error(f"Failed to query index: {e}")

    except Exception as e:
        st.error(f"Connection Failed: {e}")



    # --- Management Actions ---
    st.divider()
    st.subheader("Operation Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Management**")
        st.caption("Manage lifecycle and clean up index.")
        
        if st.button("Provision Data Store", type="secondary"):
            with st.spinner("Executing provisioning script..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "create_datastore.py"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        st.success("Provisioning complete.")
                        with st.expander("View Logs"):
                            st.code(result.stderr + "\n" + result.stdout)
                        st.rerun()
                    else:
                        st.error("Provisioning failed.")
                        with st.expander("Error Logs"):
                            st.code(result.stderr + "\n" + result.stdout)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

        if st.button("Purge Index (Delete All)", type="secondary"):
            with st.spinner("Purging all documents..."):
                try:
                    # Use default data store from config
                    purge_branch = doc_client.branch_path(
                        project=project_id,
                        location=location,
                        data_store=config.DATA_STORE_ID,
                        branch="default_branch"
                    )
                    
                    list_req = discoveryengine.ListDocumentsRequest(parent=purge_branch, page_size=1000)
                    docs = doc_client.list_documents(request=list_req)
                    
                    count = 0
                    for doc in docs:
                        doc_client.delete_document(name=doc.name)
                        count += 1
                    
                    st.success(f"Purge complete. Deleted {count} documents.")
                    st.info("Run 'Connector Sync' to repopulate.")
                    
                except Exception as e:
                    st.error(f"Purge failed: {e}")

    with col2:
        st.markdown("**Synchronization**")
        st.caption("Trigger immediate connector sync cycle.")
        if st.button("Run Connector Sync", type="primary"):
            with st.spinner("Syncing data to Vertex AI..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "connector_app.main"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        st.success("Sync complete.")
                        # Default logs go to stderr for logging module
                        with st.expander("Sync Logs"):
                            st.code(result.stderr)
                    else:
                        st.error("Sync failed.")
                        with st.expander("Error Logs"):
                            st.code(result.stderr + "\n" + result.stdout)
                except Exception as e:
                    st.error(f"Execution Error: {e}")
