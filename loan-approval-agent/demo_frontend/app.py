import streamlit as st
import json
import asyncio
import sys
import os
import uuid
import shutil
from datetime import datetime, timezone
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# --- CONFIGURATION & PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

try:
    from loan_agent.agent import loan_manager
    from loan_agent import config
    from loan_agent.tools.security import check_injection
except ImportError as e:
    st.error(f"Failed to import loan_agent: {e}")
    st.stop()

# --- STREAMLIT UI SETUP ---
st.set_page_config(
    page_title="Loan Approval Demo",
    page_icon="💰",
    layout="wide"
)

# --- GLOBAL RUNNER (Cached) ---
@st.cache_resource
def get_runner():
    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")

# Paths & State
LOG_PATH = os.path.join(BASE_DIR, "loan_agent/data/audit_logs/events.jsonl")
DECISION_DIR = os.path.join(BASE_DIR, "loan_agent/data/decisions")
# SIMULATED CUSTOMER PC (Artifacts)
CUSTOMER_PC_DIR = os.path.join(BASE_DIR, "artifacts/uploads")
# AGENT SECURE LANDING ZONE (System)
AGENT_UPLOAD_DIR = os.path.join(BASE_DIR, "loan_agent/data/uploads")

os.makedirs(DECISION_DIR, exist_ok=True)
os.makedirs(AGENT_UPLOAD_DIR, exist_ok=True)

# Data paths for scenarios
APPLICANTS_PATH = os.path.join(BASE_DIR, "external_services/data/applicants.json")
SCENARIOS_PATH = os.path.join(BASE_DIR, "demo_frontend/data/scenarios.json")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["scenario_start_time"] = datetime.now(timezone.utc).isoformat()
    st.session_state["uploaded_files"] = []

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# --- SIDEBAR: DEMO CONTROL (PERSONA: PRESENTER) ---
st.sidebar.title("🛠️ Demo Control")
st.sidebar.caption("Presenter tools for managing the live simulation.")

if st.sidebar.button("🔄 Start New Scenario", use_container_width=True, type="primary"):
    st.session_state["messages"] = []
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["scenario_start_time"] = datetime.now(timezone.utc).isoformat()
    st.session_state["uploaded_files"] = []
    # Clear system uploads for a fresh feel
    for f in os.listdir(AGENT_UPLOAD_DIR):
        os.remove(os.path.join(AGENT_UPLOAD_DIR, f))
    # Clear decisions
    for f in os.listdir(DECISION_DIR):
        os.remove(os.path.join(DECISION_DIR, f))
    st.rerun()

st.sidebar.markdown("---")

# Load and Display Scenarios from JSON
st.sidebar.subheader("📋 Scenario Selector")

def load_scenario_prompts():
    """Generates conversational prompts from JSON data."""
    try:
        with open(APPLICANTS_PATH, 'r') as f:
            applicants = {a['applicant_id']: a for a in json.load(f)}
        with open(SCENARIOS_PATH, 'r') as f:
            scenarios = json.load(f)
        
        prompts = {}
        for s in scenarios:
            app = applicants.get(s['applicant_id'], {})
            prompt = f"Hi, I'm {app.get('name', 'Applicant')}.\n\n"
            prompt += f"SSN {s['applicant_id']}. I earn ${app.get('stated_income', 0):,}\n"
            if app.get('employer'):
                prompt += f"I work at {app['employer']}.\n"
            prompt += f"${s['loan_amount']:,} for {s['purpose']}."
            
            prompts[s['name']] = prompt
        return prompts
    except Exception as e:
        st.sidebar.error(f"Error loading scenarios: {e}")
        return {}

scenario_prompts = load_scenario_prompts()
for name, prompt in scenario_prompts.items():
    with st.sidebar.expander(f"👤 {name}"):
        st.code(prompt, language="text")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Settings")
latency_mode = st.sidebar.radio("Latency:", ["TESTING", "REALISTIC"], index=0)
config.LATENCY_MODE = latency_mode

simulate_failure = st.sidebar.toggle("🚨 Simulate Credit Bureau Downtime", value=False, help="Forces the External Credit Bureau API to report downtime to test agentic resilience and retry logic.")

# --- LAYOUT ---
c_portal, c_audit = st.columns([0.6, 0.4], gap="large")

with c_audit:
    st.header("⚖️ Auditor & Oversight")
    st.caption("Live compliance monitoring and technical reasoning trace.")
    
    # Decision Records Download (Persona: Auditor)
    pdf_files = [f for f in os.listdir(DECISION_DIR) if f.endswith(".pdf")]
    pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(DECISION_DIR, x)), reverse=True)
    
    if pdf_files:
        st.subheader("📄 Compliance Artifacts")
        current_app_id = None
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                log_lines = f.readlines()
                for line in reversed(log_lines):
                    try:
                        data = json.loads(line)
                        if data.get("application_id") and data.get("application_id") != "N/A":
                            current_app_id = data["application_id"]
                            break
                    except: pass

        current_pdf = None
        if current_app_id:
            for f in pdf_files:
                if current_app_id in f:
                    current_pdf = f
                    break
        
        if current_pdf:
            st.write(f"**Current Application: {current_app_id}**")
            with open(os.path.join(DECISION_DIR, current_pdf), "rb") as f:
                st.download_button(f"⬇️ Download Decision Record ({current_app_id})", f, file_name=current_pdf, key="dl_current", type="primary", use_container_width=True)
        else:
            st.info("Waiting for final decision artifact...")

        other_pdfs = [f for f in pdf_files if f != current_pdf]
        if other_pdfs:
            with st.expander("📚 Decision History (Previous Sessions)", expanded=False):
                for pdf in other_pdfs[:5]:
                    with open(os.path.join(DECISION_DIR, pdf), "rb") as f:
                        st.download_button(f"⬇️ {pdf}", f, file_name=pdf, key=f"dl_hist_{pdf}")
        st.markdown("---")

    st.subheader("🕵️ Reasoning Trace")
    audit_placeholder = st.empty()

def render_audit_trace():
    """Renders the audit log into the placeholder, filtered by scenario start time."""
    if os.path.exists(LOG_PATH):
        start_time = st.session_state.get("scenario_start_time")
        with open(LOG_PATH, "r") as f:
            lines = f.readlines()
            content = ""
            for line in reversed(lines):
                try:
                    data = json.loads(line)
                    if start_time and data["timestamp"] < start_time:
                        continue

                    icon = "🔘"
                    evt = data["event_type"].upper()
                    if "INVESTIGATION" in evt or "CHECK" in evt: icon = "🔍"
                    if "POLICY" in evt or "DOC" in evt: icon = "📜"
                    if "DECISION" in evt: icon = "⚖️"
                    if "ERROR" in evt: icon = "❌"
                    if "DLP" in evt or "SECURITY" in evt: icon = "🛡️"
                    if "REGISTER" in evt: icon = "📝"
                    
                    content += f"**{icon} {data['event_type']}**\n\n"
                    content += f"App: {data.get('application_id', 'N/A')} | Agent: {data['agent']} | {data['timestamp']}\n\n"
                    content += f"```json\n{json.dumps(data['details'], indent=2)}\n```\n\n---\n\n"
                except: pass
            
            if content:
                audit_placeholder.markdown(content)
            else:
                audit_placeholder.info("Waiting for agent activity...")
    else:
        audit_placeholder.info("Waiting for agent activity...")

async def run_agent(text_input, response_placeholder):
    """Async generator to run the agent and update the UI."""
    runner = get_runner()
    
    # 1. PRE-PROCESSING SECURITY CHECK
    if check_injection(text_input, applicant_id="demo_user"):
        st.error("🚨 Security Alert: Potential prompt injection or system override detected. Transaction halted.")
        render_audit_trace()
        return "SECURITY_VIOLATION"

    # 2. Session Management
    session = await runner.session_service.get_session(
        app_name=runner.app_name, user_id="demo_user", session_id=st.session_state["session_id"]
    )
    if not session:
        await runner.session_service.create_session(
            app_name=runner.app_name, user_id="demo_user", session_id=st.session_state["session_id"]
        )

    full_resp = ""
    # Append info about uploaded files and failure mode
    files_info = ""
    if st.session_state.get("uploaded_files"):
        files_info += f"\n[User has uploaded the following documents to the secure system: {', '.join(st.session_state['uploaded_files'])}]"
    
    if simulate_failure:
        files_info += "\n[SYSTEM ALERT: External Credit Bureau API is currently reporting DOWNTIME. All calls will fail. The system is configured with exponential backoff (5 retries). Toggling this switch OFF will allow the next retry to succeed.]"
    
    user_content = UserContent(parts=[Part(text=text_input + files_info)])
    
    async for event in runner.run_async(
        user_id="demo_user",
        session_id=st.session_state["session_id"],
        new_message=user_content
    ):
        render_audit_trace()
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_resp += part.text
                    response_placeholder.markdown(full_resp + "▌")
    
    response_placeholder.markdown(full_resp)
    return full_resp

with c_portal:
    st.title("💰 FastLoan Portal")
    st.caption("Persona: Simulated Applicant")
    st.divider()

    chat_history = st.container(height=500)
    
    with chat_history:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Document Upload (Persona: Applicant)
    st.markdown("---")
    with st.expander("📤 Attach Documents (Bank Statement / ID)", expanded=False):
        # We simulate selecting a file from the "Customer PC"
        available_files = [f for f in os.listdir(CUSTOMER_PC_DIR) if f.endswith(".pdf")]
        selected_file = st.selectbox("Select file from local disk:", [""] + available_files)
        
        if selected_file:
            # Simulation: Copy from PC to System Upload Zone
            src_path = os.path.join(CUSTOMER_PC_DIR, selected_file)
            dst_path = os.path.join(AGENT_UPLOAD_DIR, selected_file)
            shutil.copy(src_path, dst_path)
            
            if selected_file not in st.session_state["uploaded_files"]:
                st.session_state["uploaded_files"].append(selected_file)
                st.toast(f"File uploaded to secure portal: {selected_file}")
                
                st.session_state["messages"].append({"role": "user", "content": f"[Attached: {selected_file}]"})
                with chat_history:
                    with st.chat_message("assistant"):
                        ph = st.empty()
                        resp = asyncio.run(run_agent(f"I have just uploaded {selected_file} to the portal. Please process it.", ph))
                        if resp != "SECURITY_VIOLATION":
                            st.session_state["messages"].append({"role": "assistant", "content": resp})
                            st.rerun()

    # Auto-Greeting
    if not st.session_state["messages"]:
        with chat_history:
            with st.chat_message("assistant"):
                ph = st.empty()
                resp = asyncio.run(run_agent("I am here to apply for a loan. Please greet me.", ph))
                st.session_state["messages"].append({"role": "assistant", "content": resp})
                st.rerun()

    if prompt_text := st.chat_input("Tell us about your loan request..."):
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        st.rerun()

    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        last_msg = st.session_state["messages"][-1]["content"]
        with chat_history:
            with st.chat_message("assistant"):
                ph = st.empty()
                resp = asyncio.run(run_agent(last_msg, ph))
                if resp != "SECURITY_VIOLATION":
                    st.session_state["messages"].append({"role": "assistant", "content": resp})
                    st.rerun()

# Final static render
render_audit_trace()
