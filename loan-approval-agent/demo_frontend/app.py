import streamlit as st
import json
import asyncio
import sys
import os
import uuid
import shutil
import threading
import queue
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
    from external_services.simulation_utils import set_service_failure
except ImportError as e:
    st.error(f"Failed to import loan_agent: {e}")
    st.stop()

# --- STREAMLIT UI SETUP ---
st.set_page_config(
    page_title="Loan Approval Demo",
    page_icon="💰",
    layout="wide"
)

from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_ctx, get_script_run_ctx

# --- PERSISTENT BACKGROUND LOOP FOR AGENTS ---
# This ensures that cached ADK objects always see the same event loop.
@st.cache_resource
def get_agent_event_loop():
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True, name="AgentLoopThread")
    # We don't add script context to the LOOP thread itself, 
    # but we will add it to the TASK thread/coro when it runs.
    thread.start()
    return loop, thread

def run_async_on_agent_loop(coro):
    """Bridge for simple coroutines."""
    loop, _ = get_agent_event_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

def run_agent_generator_bridge(text_input, response_placeholder):
    """Bridge for the agent run (AsyncGenerator -> Streamlit UI)."""
    loop, _ = get_agent_event_loop()
    ctx = get_script_run_ctx() # Get current UI context
    q = queue.Queue()
    
    # This wrapper will run ON the background loop
    async def agent_task():
        # Attach the UI context to this task's execution thread (if possible)
        # or at least ensure it's available for libraries that check it.
        if ctx:
            add_script_run_ctx(threading.current_thread(), ctx)
        
        try:
            async for event in run_agent(text_input):
                q.put(("event", event))
            q.put(("done", None))
        except Exception as e:
            import traceback
            traceback.print_exc()
            q.put(("error", str(e)))

    asyncio.run_coroutine_threadsafe(agent_task(), loop)
    
    # This loop runs ON the Streamlit thread
    full_resp = ""
    while True:
        try:
            msg_type, val = q.get(timeout=1.0) # Check for events every second
            if msg_type == "event":
                if val == "SECURITY_VIOLATION":
                    st.error("🚨 Security Alert: Potential prompt injection or system override detected.")
                    return "SECURITY_VIOLATION"
                
                # Update UI
                full_resp = val
                response_placeholder.markdown(full_resp + "▌")
                
            elif msg_type == "done":
                response_placeholder.markdown(full_resp)
                return full_resp
            elif msg_type == "error":
                st.error(f"Agent Error: {val}")
                return f"ERROR: {val}"
        except queue.Empty:
            # On timeout, just refresh the audit trace and keep waiting
            pass
        
        # Refresh audit trace on every iteration (event or timeout)
        render_audit_trace()

# --- GLOBAL RUNNER (Cached) ---
@st.cache_resource(show_spinner=False)
def get_runner():
    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")

async def run_agent(text_input):
    """
    Async generator to run the agent. 
    MUST be called from the agent background loop.
    """
    runner = get_runner()
    
    # 1. PRE-PROCESSING SECURITY CHECK
    if check_injection(text_input, applicant_id="demo_user"):
        yield "SECURITY_VIOLATION"
        return

    # 2. Session Management
    session = await runner.session_service.get_session(
        app_name=runner.app_name, user_id="demo_user", session_id=st.session_state["session_id"]
    )
    if not session:
        await runner.session_service.create_session(
            app_name=runner.app_name, user_id="demo_user", session_id=st.session_state["session_id"]
        )

    full_resp = ""
    files_info = ""
    if st.session_state.get("uploaded_files"):
        files_info += f"\n[User has uploaded the following documents to the secure system: {', '.join(st.session_state['uploaded_files'])}]"
    
    user_content = UserContent(parts=[Part(text=text_input + files_info)])
    
    async for event in runner.run_async(
        user_id="demo_user",
        session_id=st.session_state["session_id"],
        new_message=user_content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_resp += part.text
                    yield full_resp

# Paths & State
LOG_PATH = os.path.join(BASE_DIR, "loan_agent/data/audit_logs/events.jsonl")
DECISION_DIR = os.path.join(BASE_DIR, "loan_agent/data/decisions")
CUSTOMER_PC_DIR = os.path.join(BASE_DIR, "artifacts/uploads")
AGENT_UPLOAD_DIR = os.path.join(BASE_DIR, "loan_agent/data/uploads")

os.makedirs(DECISION_DIR, exist_ok=True)
os.makedirs(AGENT_UPLOAD_DIR, exist_ok=True)

APPLICANTS_PATH = os.path.join(BASE_DIR, "external_services/data/applicants.json")
SCENARIOS_PATH = os.path.join(BASE_DIR, "demo_frontend/data/scenarios.json")

def get_now_ts():
    """Matches the timestamp format in audit_logger.py exactly."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{round(now.microsecond / 100000) % 10}"

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["scenario_start_time"] = get_now_ts()
    st.session_state["uploaded_files"] = []

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "simulate_failure" not in st.session_state:
    st.session_state["simulate_failure"] = False

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

# --- SIDEBAR: DEMO CONTROL ---
st.sidebar.title("🛠️ Demo Control")
st.sidebar.caption("Presenter tools for managing the live simulation.")

if st.sidebar.button("🔄 Start New Scenario", use_container_width=True, type="primary"):
    st.session_state["messages"] = []
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["scenario_start_time"] = get_now_ts()
    st.session_state["uploaded_files"] = []
    st.session_state["uploader_key"] += 1
    for f in os.listdir(AGENT_UPLOAD_DIR):
        os.remove(os.path.join(AGENT_UPLOAD_DIR, f))
    for f in os.listdir(DECISION_DIR):
        os.remove(os.path.join(DECISION_DIR, f))
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Scenario Selector")

def load_scenario_prompts():
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
            purpose = s['purpose']
            if purpose.startswith("to "):
                prompt += f"${s['loan_amount']:,} {purpose}."
            elif purpose.startswith("buy "): # Special case for the yacht
                prompt += f"${s['loan_amount']:,} to {purpose}."
            else:
                prompt += f"${s['loan_amount']:,} for {purpose}."
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

st.sidebar.toggle("🚨 Simulate Credit Bureau Downtime", key="simulate_failure")
set_service_failure("credit_bureau", st.session_state["simulate_failure"])

# --- LAYOUT ---
c_portal, c_audit = st.columns([0.6, 0.4], gap="large")

with c_audit:
    st.header("⚖️ Auditor & Oversight")
    st.caption("Live compliance monitoring and technical reasoning trace.")
    
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

    st.subheader("🕵️ Reasoning Trace")
    audit_placeholder = st.empty()

def render_audit_trace():
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
                    icon = "🔍" if "INVESTIGATION" in data["event_type"].upper() else "🔘"
                    content += f"**{icon} {data['event_type']}**\n\n"
                    content += f"App: {data.get('application_id', 'N/A')} | Agent: {data['agent']} | {data['timestamp']}\n\n"
                    content += f"```json\n{json.dumps(data['details'], indent=2)}\n```\n\n---\n\n"
                except: pass
            audit_placeholder.markdown(content if content else "Waiting for agent activity...")

with c_portal:
    st.title("💰 FastLoan Portal")
    chat_history = st.container(height=500)
    
    with chat_history:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    st.markdown("---")
    with st.expander("📤 Upload Documents", expanded=False):
        uploaded_file = st.file_uploader("Upload a PDF document:", type=["pdf"], key=f"uploader_{st.session_state['uploader_key']}")
        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_path = os.path.join(AGENT_UPLOAD_DIR, file_name)
            
            # Save the file to the agent's upload directory
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            if file_name not in st.session_state["uploaded_files"]:
                st.session_state["uploaded_files"].append(file_name)
                st.session_state["messages"].append({"role": "user", "content": f"[Uploaded: {file_name}]"})
                with chat_history:
                    with st.chat_message("assistant"):
                        resp = run_agent_generator_bridge(f"I have just uploaded {file_name}. Please analyze it for the loan application.", st.empty())
                        if resp != "SECURITY_VIOLATION":
                            st.session_state["messages"].append({"role": "assistant", "content": resp})
                            st.rerun()

    if not st.session_state["messages"]:
        with chat_history:
            with st.chat_message("assistant"):
                resp = run_agent_generator_bridge("Greet me.", st.empty())
                st.session_state["messages"].append({"role": "assistant", "content": resp})
                st.rerun()

    if prompt_text := st.chat_input("Message..."):
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        st.rerun()

    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        last_msg = st.session_state["messages"][-1]["content"]
        with chat_history:
            with st.chat_message("assistant"):
                resp = run_agent_generator_bridge(last_msg, st.empty())
                if resp != "SECURITY_VIOLATION":
                    st.session_state["messages"].append({"role": "assistant", "content": resp})
                    st.rerun()

render_audit_trace()
