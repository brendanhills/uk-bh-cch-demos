import streamlit as st
import json
import asyncio
import sys
import os
import shutil
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# Ensure we are in the project root
sys.path.append(os.getcwd())

# Import config to load environment variables
from loan_approval_agent import config
from loan_approval_agent.agent import loan_manager
from loan_approval_agent.tools.intake import register_application as register_application_base
from loan_approval_agent.tools import token_vault
from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent.tools.security import check_injection

st.set_page_config(page_title="Fintech Loan Agent", layout="wide")

# Wrapper for register_application to update Streamlit state
def register_application(name: str, gov_id: str, income: int, employer: str, amount: int, purpose: str):
    """Local wrapper that updates session state when the agent calls the tool."""
    result = register_application_base(name, gov_id, income, employer, amount, purpose)
    if result.get("status") == "success":
        st.session_state["form_data"] = {
            "name": name,
            "application_id": result.get("application_id"),
            "applicant_id": result.get("applicant_id"),
            "income": income,
            "employer": employer,
            "amount": amount,
            "purpose": purpose
        }
        st.session_state["submitted"] = True
    return result

st.title("🤖 Fintech Loan Approval Agent")
st.markdown("### AI-Powered Underwriting Demo")

# Mock Data for Demo
# Load Demo Data
# Load Demo Data
# Resolve path robustly relative to THIS file
# --- CONFIGURATION & PATHS ---
# Robustly resolve paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_DATA_DIR = os.path.join(BASE_DIR, "loan_approval_agent/data/demo_data")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "loan_approval_agent/data/audit_logs/events.jsonl")

def load_json_data(filename):
    """Safe JSON loader for demo data."""
    path = os.path.join(DEMO_DATA_DIR, filename)
    if not os.path.exists(path):
        st.error(f"File not found: {path}")
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return []

# Load applicants
raw_applicants = load_json_data("applicants.json")
applicants = {}
if isinstance(raw_applicants, list):
    for a in raw_applicants:
        if "applicant_id" in a:
            applicants[a["applicant_id"]] = a
elif isinstance(raw_applicants, dict):
    applicants = raw_applicants

scenarios = load_json_data("scenarios.json")

def clear_session_state():
    """Completely resets the application state for a fresh start."""
    st.session_state.clear()
    st.session_state["initialized"] = True
    
    # Truncate Audit Log for fresh demo
    if os.path.exists(AUDIT_LOG_FILE):
         open(AUDIT_LOG_FILE, "w").close()

# Sidebar: Demo Controller
with st.sidebar:
    st.header("🎮 Demo Controller")
    
    if st.button("🔄 Start New Application", use_container_width=True):
        clear_session_state()
        st.rerun()
    
    st.divider()

    # 1. Scenario Selector
    st.subheader("1. Scenarios")
    scenario_options = {s["name"]: s for s in scenarios}
    selected_scenario_name = st.selectbox(
        "Select Scenario",
        ["Choose..."] + list(scenario_options.keys())
    )
    
    if selected_scenario_name != "Choose...":
        s = scenario_options[selected_scenario_name]
        a = applicants.get(s["applicant_id"])
        
        st.info(f"Loaded: {s['name']}")
        
        if st.button("⚡ Quick Fill Form"):
            if a:
                clear_session_state()

                # 2. Inject the message
                quick_msg = (
                    f"Hi, I am {a['name']}. "
                    f"My Government ID is {s['applicant_id']}. "
                    f"I earn {a['stated_income']} USD working at {a['employer']}. "
                    f"I would like to borrow {s['loan_amount']} USD for {s['purpose']}."
                )
                st.session_state["auto_input"] = quick_msg
                st.rerun()
            else:
                st.error("Applicant data not found!")

        # Manual Entry Details
        if a:
            with st.expander("️ Scenario Details (Admin View)", expanded=True):
                st.info(f"Roleplay as: **{a['name']}**")
                
                # Hidden ID
                st.caption("Government ID (SSN):")
                st.code(s["applicant_id"], language="text")
                
                st.text_input("Name", value=a["name"], disabled=True)
                st.text_input("Income", value=str(a["stated_income"]), disabled=True)
                st.text_input("Employer", value=a["employer"], disabled=True)
                st.text_input("Amount", value=str(s["loan_amount"]), disabled=True)
                st.text_input("Purpose", value=s["purpose"], disabled=True)
        else:
            st.warning("Applicant details missing for this scenario.")



    # 2. Controls
    st.subheader("2. Controls")
    
    latency_mode = st.radio(
        "Latency Simulation",
        ["REALISTIC", "TESTING"],
        index=1,
        help="REALISTIC adds delays to tools."
    )
    config.LATENCY_MODE = latency_mode

    st.divider()

    # 3. Policy Hot-Swap (X-Factor)
    st.subheader("3. Agility (X-Factor)")
    policy_mode = st.radio("Active Policy", ["Standard (Conservative)", "Growth (Aggressive)"])
    if policy_mode == "Growth (Aggressive)":
        st.caption("✅ Growth Policy Active: Allows thinner files and higher DTI.")
        # In a real app, this would swap the PDF file in data/policy_docs
        # For demo, we can set a session flag or env var
        os.environ["POLICY_MODE"] = "GROWTH"
    else:
        os.environ["POLICY_MODE"] = "STANDARD"

    with st.expander("🔍 Debug State"):
        st.json(st.session_state)

# Initialize Session State
if "initialized" not in st.session_state:
    # Truncate Audit Log on first launch
    if os.path.exists(AUDIT_LOG_FILE):
        open(AUDIT_LOG_FILE, "w").close()
    st.session_state["initialized"] = True

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome to the Loan Portal! I can help you submit a new application. To begin, please tell me your full name."}]
if "intake_step" not in st.session_state:
    st.session_state["intake_step"] = 0
if "form_data" not in st.session_state:
    st.session_state["form_data"] = {}

# Tools for Agent-Driven Intake
# The register_application function is now imported from loan_approval_agent.tools.intake
# It handles the tokenization internally.

# Initialize Loan Manager & Tools
# We need to ensure we don't add the tool repeatedly on rerun
# Initialize Loan Manager & Tools
# Ensure we use the CURRENT 'register_application' function (fresh closure over st.session_state)
# Remove any existing instance of the tool (from previous runs/reloads)
loan_manager.tools = [t for t in loan_manager.tools if getattr(t, "__name__", str(t)) != "register_application"]
# Add the fresh tool instance
loan_manager.tools.append(register_application)
st.session_state["intake_agent_setup"] = True

# Helper to get runner
@st.cache_resource
def get_runner():
    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")

runner = get_runner()

# --- LAYOUT SETUP ---
c_main, c_audit = st.columns([0.65, 0.35], gap="large")

# --- AUDIT LOG (Always Visible) ---
with c_audit:
    st.subheader("📜 Live Audit Log")
    # Use a scrolling container but put a placeholder inside that we can reliably clear
    log_scroll_area = st.container(height=700)
    with log_scroll_area:
        log_container = st.empty()

def render_audit_log(placeholder):
    with placeholder.container():
        if os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, "r") as f:
                lines = f.readlines()
                # Show last 100 events, newest on top
                for line in reversed(lines[-100:]):
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                        agent = event.get('agent', 'System')
                        app_id_str = f" | {event.get('application_id')}" if event.get('application_id') else ""
                        st.caption(f"{event.get('timestamp', '')[11:19]} - **{agent}**{app_id_str}: {event.get('event_type')} ")
                        st.json(event.get("details"), expanded=False)
                        st.divider()
                    except:
                        st.text(line)
        else:
            st.info("No audit logs found yet.")

# Initial Render of Log
render_audit_log(log_container)

# --- MAIN INTERFACE ---
with c_main:
    # 1. Dashboard (Only after submission)
    if st.session_state.get("submitted"):
        data = st.session_state["form_data"]
        c1, c2 = st.columns(2)
        app_id = data.get("application_id", "Unknown")
        token_id = data.get("applicant_id", "Unknown")
        
        with c1:
            st.markdown(f"**Applicant**: {data.get('name')}")
            st.markdown(f"**Application ID**: `{app_id}`")
            st.markdown(f"**Applicant ID (Token)**: `{token_id}`")
            st.markdown(f"**Employer**: {data.get('employer')}")
            
        with c2:
            st.markdown(f"**Income**: ${data.get('income', 0):,}")
            st.markdown(f"**Loan Amount**: ${data.get('amount', 0):,}")
            st.markdown(f"**Purpose**: {data.get('purpose')}")
        
        st.divider()

        # Security check logic
        if "security_checked" not in st.session_state:
            with st.spinner("🛡️ Running Security Scan..."):
                user_input = f"{data.get('purpose', '')} {data.get('name', '')}"
                if check_injection(user_input):
                    st.error("🚨 SECURITY ALERT: Prompt Injection Detected!")
                    st.stop()
                else:
                    st.session_state["security_checked"] = True
                    st.rerun()

    # 2. Chat History (Shared for both phases)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["messages"]:
            if msg.get("role") == "tool_call":
                with st.status(msg["content"], state="complete"):
                    pass
            else:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"] + "\n")
                    # Check for "Final Decision" to show success/error/warning icons
                    if msg["role"] == "assistant" and "Final Decision" in msg["content"]:
                        if "APPROVE" in msg["content"]: st.success("✅ Approved")
                        elif "DENY" in msg["content"]: st.error("❌ Denied")
                        elif "ESCALATE" in msg["content"]: st.warning("⚠️ Escalated")

    # 3. Input Handling
    if not st.session_state.get("submitted"):
        # INTAKE PHASE INPUT
        if "auto_input" in st.session_state:
            prompt = st.session_state.pop("auto_input")
        else:
            prompt = st.chat_input("Enter your details...")

        if prompt:
            with chat_container:
                with st.chat_message("user"):
                    st.write(prompt)
            st.session_state["messages"].append({"role": "user", "content": prompt})
            
            log_event("Guest", "Intake_Processing_Start", {"input_length": len(prompt)})
            
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        if "agent_session_id" not in st.session_state:
                            session = asyncio.run(runner.session_service.create_session(user_id="demo_user", app_name="loan_agent"))
                            st.session_state["agent_session_id"] = session.id
                        else:
                            session = asyncio.run(runner.session_service.get_session(session_id=st.session_state["agent_session_id"], user_id="demo_user", app_name="loan_agent"))

                        placeholder = st.empty()
                        response_container = {"text": ""}

                        async def run_chat():
                            async for event in runner.run_async(
                                session_id=session.id,
                                user_id="demo_user",
                                new_message=UserContent(parts=[Part(text=prompt)])
                            ):
                                if hasattr(event, "content") and event.content:
                                    parts = [p.text for p in event.content.parts if p.text]
                                    if parts:
                                        text = "".join(parts)
                                        response_container["text"] += text
                                        placeholder.markdown(response_container["text"] + "▌")
                                        
                                if hasattr(event, "tool_calls") and event.tool_calls:
                                     for tc in event.tool_calls:
                                         for fc in tc.function_calls:
                                             msg_content = f"🛠️ Executing {fc.name}..."
                                             st.session_state["messages"].append({"role": "tool_call", "content": msg_content})
                                             with st.status(msg_content, state="complete"):
                                                 pass
                                render_audit_log(log_container)
                        
                        asyncio.run(run_chat())
                        full_response = response_container["text"]
                        placeholder.markdown(full_response)
                        st.session_state["messages"].append({"role": "assistant", "content": full_response})
                        
                        if st.session_state.get("submitted"):
                            st.rerun()
    else:
        # ANALYSIS PHASE / HITL INPUT
        if reply := st.chat_input("Response..."):
            with chat_container:
                with st.chat_message("user"):
                    st.write(reply)
            st.session_state["messages"].append({"role": "user", "content": reply})
            
            @st.cache_resource
            def get_runner_analysis():
                return InMemoryRunner(agent=loan_manager, app_name="loan_agent")
            runner_analysis = get_runner_analysis()

            async def execute_run_hitl(input_text):
                if "analysis_session_id" not in st.session_state:
                    # Continue using intake session
                    st.session_state["analysis_session_id"] = st.session_state["agent_session_id"]
                
                session = await runner_analysis.session_service.get_session(st.session_state["analysis_session_id"])
                
                with chat_container:
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        full_text = ""
                        async for event in runner_analysis.run_async(
                            session_id=session.id,
                            user_id="demo_user",
                            new_message=UserContent(parts=[Part(text=input_text)])
                        ):
                            if hasattr(event, "content") and event.content:
                                text = "".join([p.text for p in event.content.parts if p.text])
                                full_text += text
                                placeholder.markdown(full_text + "▌")
                            elif hasattr(event, "tool_calls") and event.tool_calls:
                                for tc in event.tool_calls:
                                    for fc in tc.function_calls:
                                        msg_content = f"🛠️ Executing {fc.name}..."
                                        st.session_state["messages"].append({"role": "tool_call", "content": msg_content})
                                        with st.status(msg_content, state="complete"):
                                            pass
                            render_audit_log(log_container)
                        placeholder.markdown(full_text)
                        st.session_state["messages"].append({"role": "assistant", "content": full_text})

            asyncio.run(execute_run_hitl(reply))
            st.rerun()

        # 4. Supporting Documents (Positioned between Input and Record)
        # Hide if a final decision has been reached
        decision_reached = any(any(x in m["content"] for x in ["APPROVE", "DENY", "ESCALATE"]) 
                               for m in st.session_state["messages"] if m["role"] == "assistant" and "Final Decision" in m["content"])
        
        if not decision_reached:
            st.divider()
            st.subheader("📁 Supporting Documents")
            
            uploaded_file = st.file_uploader(
                "Upload Pay Stubs or Bank Statements", 
                type=["pdf", "png", "jpg"], 
                key="doc_uploader",
                help="Upload documents for agent analysis."
            )
            
            if uploaded_file:
                upload_dir = os.path.join(BASE_DIR, "loan_approval_agent/data/uploads")
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded: `{uploaded_file.name}`")
                st.info(f"💡 **Tip**: Tell the agent: 'I have uploaded my pay stub. Please analyze it from `{save_path}`'")

        # Decision PDF Download
        decisions_dir = os.path.join(BASE_DIR, "data/decisions")
        if os.path.exists(decisions_dir):
            data = st.session_state["form_data"]
            # Search by Application ID first, then Applicant Token
            pdf_files = [f for f in os.listdir(decisions_dir) if f.endswith(".pdf") and 
                         (data.get("application_id") in f or data.get("applicant_id") in f)]
            pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(decisions_dir, x)), reverse=True)
            if pdf_files:
                st.divider()
                st.subheader("📄 Decision Record (Compliance)")
                latest_pdf = pdf_files[0]
                with open(os.path.join(decisions_dir, latest_pdf), "rb") as f:
                    st.download_button("📥 Download Decision Record (PDF)", f.read(), latest_pdf, "application/pdf")

