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

# --- GLOBAL RUNNER ---
def get_runner():
    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")

# --- PATHS & STATE ---
LOG_PATH = os.path.join(BASE_DIR, "loan_agent/data/audit_logs/events.jsonl")
DECISION_DIR = os.path.join(BASE_DIR, "loan_agent/data/decisions")
os.makedirs(DECISION_DIR, exist_ok=True)

# Data paths for scenarios
# External Source of Truth
APPLICANTS_PATH = os.path.join(BASE_DIR, "external_services/data/applicants.json")
# Demo-specific scenario configuration
SCENARIOS_PATH = os.path.join(BASE_DIR, "demo_frontend/data/scenarios.json")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["scenario_start_time"] = datetime.now(timezone.utc).isoformat()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# --- SIDEBAR: DEMO CONTROL ---
st.sidebar.title("🛠️ Demo Control")
st.sidebar.caption("Presenter tools (Not part of the UI)")

if st.sidebar.button("🔄 Start New Scenario", use_container_width=True, type="primary"):
    st.session_state["messages"] = []
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["scenario_start_time"] = datetime.now(timezone.utc).isoformat()
    # Clear decisions for a fresh feel
    for f in os.listdir(DECISION_DIR):
        os.remove(os.path.join(DECISION_DIR, f))
    st.rerun()

st.sidebar.markdown("---")

# Load and Display Scenarios from JSON
st.sidebar.subheader("📋 Demo Scenarios")

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

# Decision Records Download
pdf_files = sorted([f for f in os.listdir(DECISION_DIR) if f.endswith(".pdf")], reverse=True)
if pdf_files:
    st.sidebar.subheader("📄 Generated Records")
    for pdf in pdf_files[:3]:
        with open(os.path.join(DECISION_DIR, pdf), "rb") as f:
            st.sidebar.download_button(f"⬇️ {pdf}", f, file_name=pdf, key=f"dl_{pdf}")
    st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ Settings")
latency_mode = st.sidebar.radio("Latency:", ["TESTING", "REALISTIC"], index=0)
config.LATENCY_MODE = latency_mode

# --- LAYOUT ---
c_main, c_audit_col = st.columns([0.65, 0.35], gap="large")

with c_audit_col:
    st.subheader("🕵️ Audit Trace")
    st.caption("Live audit log of all agent actions and tool calls")
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
    # We demonstrate proactive protection against prompt injection
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
    user_content = UserContent(parts=[Part(text=text_input)])
    
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

with c_main:
    st.title("💰 FastLoan Portal")
    st.caption("Apply for your personal loan in seconds.")

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Auto-Greeting
    if not st.session_state["messages"]:
        with st.chat_message("assistant"):
            ph = st.empty()
            resp = asyncio.run(run_agent("I am here to apply for a loan. Please greet me.", ph))
            st.session_state["messages"].append({"role": "assistant", "content": resp})
            st.rerun()

    # User Input
    if prompt_text := st.chat_input("Tell us about your loan request..."):
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        with st.chat_message("user"):
            st.markdown(prompt_text)

        with st.chat_message("assistant"):
            ph = st.empty()
            resp = asyncio.run(run_agent(prompt_text, ph))
            st.session_state["messages"].append({"role": "assistant", "content": resp})
            st.rerun()

# Final static render
render_audit_trace()
