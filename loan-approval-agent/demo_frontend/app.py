import streamlit as st
import json
import asyncio
import sys
import os
import uuid
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
UPLOAD_DIR = os.path.join(BASE_DIR, "artifacts/uploads")
os.makedirs(DECISION_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    # Clear decisions for a fresh feel
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

# --- LAYOUT ---
c_portal, c_audit = st.columns([0.6, 0.4], gap="large")

with c_audit:
    st.header("⚖️ Auditor & Oversight")
    st.caption("Live compliance monitoring and technical reasoning trace.")
    
    # Decision Records Download (Persona: Auditor)
    pdf_files = [f for f in os.listdir(DECISION_DIR) if f.endswith(".pdf")]
    # Sort by modification time (mtime) - most recent first
    pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(DECISION_DIR, x)), reverse=True)
    
    if pdf_files:
        st.subheader("📄 Compliance Artifacts")
        # Show top 5 most recent
        for pdf in pdf_files[:5]:
            with open(os.path.join(DECISION_DIR, pdf), "rb") as f:
                st.download_button(f"⬇️ {pdf}", f, file_name=pdf, key=f"dl_{pdf}")
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
    # Append info about uploaded files to the context if they exist
    files_info = ""
    if st.session_state.get("uploaded_files"):
        files_info = f"\n[User has uploaded the following documents: {', '.join(st.session_state['uploaded_files'])}]"
    
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

    # Container for chat history to keep it separate from the bottom widgets
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Document Upload (Persona: Applicant) - Placed in the flow
    st.markdown("---")
    with st.expander("📤 Attach Documents (Bank Statement / ID)", expanded=False):
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg"], label_visibility="collapsed")
        if uploaded_file:
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File uploaded: {uploaded_file.name}")
            if uploaded_file.name not in st.session_state["uploaded_files"]:
                st.session_state["uploaded_files"].append(uploaded_file.name)

    # Auto-Greeting (Check if first run)
    if not st.session_state["messages"]:
        with chat_container:
            with st.chat_message("assistant"):
                ph = st.empty()
                resp = asyncio.run(run_agent("I am here to apply for a loan. Please greet me.", ph))
                st.session_state["messages"].append({"role": "assistant", "content": resp})
                st.rerun()

    # User Input - st.chat_input automatically pins to the bottom of the PAGE or current CONTAINER.
    # However, to ensure it doesn't appear "above" the recent input during the run loop,
    # we handle it carefully here.
    if prompt_text := st.chat_input("Tell us about your loan request..."):
        # Immediately display the user's message in the history
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        
        # Redraw to show the user message immediately
        st.rerun()

    # If the last message is from the user, trigger the assistant
    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        last_user_message = st.session_state["messages"][-1]["content"]
        with chat_container:
            with st.chat_message("assistant"):
                ph = st.empty()
                resp = asyncio.run(run_agent(last_user_message, ph))
                if resp != "SECURITY_VIOLATION":
                    st.session_state["messages"].append({"role": "assistant", "content": resp})
                    st.rerun()

# Final static render
render_audit_trace()
