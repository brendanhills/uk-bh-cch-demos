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
from loan_approval_agent.tools.intake import submit_application
from loan_approval_agent.tools import token_vault
from loan_approval_agent.tools.audit_logger import log_event

st.set_page_config(page_title="Fintech Loan Agent", layout="wide")



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

# Sidebar: Demo Controller
with st.sidebar:
    st.header("🎮 Demo Controller")
    
    if st.button("🔄 Start New Application", use_container_width=True):
        # Clear all state
        for key in ["form_data", "submitted", "trace_events", "trace_index", "messages", "intake_step", "analysis_session_id", "agent_session_id", "security_checked", "agent_started"]:
            if key in st.session_state:
                del st.session_state[key]
        
        # Truncate Audit Log for fresh demo
        if os.path.exists(AUDIT_LOG_FILE):
             open(AUDIT_LOG_FILE, "w").close()
                
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
                # 1. Clear existing session for a fresh start (like Start New App)
                for key in ["form_data", "submitted", "trace_events", "trace_index", "messages", "intake_step", "agent_started"]:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # 2. Inject the message
                quick_msg = (
                    f"Hi, I am {a['name']}. "
                    f"My Government ID is {s['applicant_id']}. "
                    f"I earn {a['stated_income']} USD working at {a['employer']}. "
                    f"I would like to borrow {s['loan_amount']} USD to {s['purpose']}."
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
    step_through = st.checkbox("Step-Through Mode", value=False, help="Pause after each agent step.")
    
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
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I am the Loan Manager. Please enter your **full name** to begin the verification process."}]
if "intake_step" not in st.session_state:
    st.session_state["intake_step"] = 0
if "form_data" not in st.session_state:
    st.session_state["form_data"] = {}

# Tools for Agent-Driven Intake
# The submit_application function is now imported from loan_approval_agent.tools.intake
# It handles the tokenization internally.

# Initialize Loan Manager & Tools
# We need to ensure we don't add the tool repeatedly on rerun
# Initialize Loan Manager & Tools
# Ensure we use the CURRENT 'submit_application' function (fresh closure over st.session_state)
# Remove any existing instance of the tool (from previous runs/reloads)
loan_manager.tools = [t for t in loan_manager.tools if getattr(t, "__name__", str(t)) != "submit_application"]
# Add the fresh tool instance
loan_manager.tools.append(submit_application)
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
    log_container = st.container(height=700)

def render_audit_log(container):
    container.empty()
    with container:
        if os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, "r") as f:
                lines = f.readlines()
                # Show last 20 events, newest on top
                for line in reversed(lines[-20:]):
                    try:
                        event = json.loads(line)
                        st.caption(f"{event.get('timestamp', '')[11:19]} - **{event.get('event_type')}**")
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
    # Chat Interface (Intake)
    if not st.session_state.get("submitted"):
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "Welcome to the Loan Portal! I can help you submit a new application. To begin, please tell me your full name."}
            ]

        # 1. Container for Chat History (ensures messages appear above input)
        chat_container = st.container()
        
        # 2. Input Handling (at bottom of column)
        if "auto_input" in st.session_state:
            prompt = st.session_state.pop("auto_input")
        else:
            prompt = st.chat_input("Answer the agent...")

        # 3. Render Content inside Container
        with chat_container:
            # Display History
            for msg in st.session_state["messages"]:
                if msg.get("role") == "tool_call":
                   with st.status(msg["content"], state="complete"):
                       pass
                else: 
                   with st.chat_message(msg["role"]):
                       st.write(msg["content"])

            # Handle New Input
            if prompt:
                # 1. User Message
                with st.chat_message("user"):
                    st.write(prompt)
                st.session_state["messages"].append({"role": "user", "content": prompt})

                # 2. Log Start of Processing
                # "Guest" until we have an ID
                log_event("Guest", "Intake_Processing_Start", {"input_length": len(prompt)})
                render_audit_log(log_container)

                # 3. Agent Response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Ensure Session
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
                                             with st.status(msg_content, state="running"):
                                                 render_audit_log(log_container)
                                                 pass
                                                 
                        asyncio.run(run_chat())
                        full_response = response_container["text"]
                        placeholder.markdown(full_response)
                        st.session_state["messages"].append({"role": "assistant", "content": full_response})
                        
                        if st.session_state.get("submitted"):
                            st.rerun()

    # Analysis Phase (Dashboard)
    if st.session_state.get("submitted"):
        data = st.session_state["form_data"]
        
        c1, c2 = st.columns(2)
        app_id = data.get("applicant_id", "Unknown")
        
        with c1:
            st.markdown(f"**Applicant**: {data.get('name')}")
            st.markdown(f"**ID**: `{app_id}`")
            st.markdown(f"**Employer**: {data.get('employer')}")
            
        with c2:
            st.markdown(f"**Income**: ${data.get('income', 0):,}")
            st.markdown(f"**Loan Amount**: ${data.get('amount', 0):,}")
            st.markdown(f"**Purpose**: {data.get('purpose')}")
        
        st.divider()
        
        if not app_id or app_id == "Unknown":
            st.error("❌ Applicant ID is missing. Please restart the application.")
        else:
            # 1. SECURITY CHECK (X-Factor) - Moved here to be part of the initial submission flow
            if "security_checked" not in st.session_state:
                with st.spinner("🛡️ Running Security Scan..."):
                    user_input = f"{data.get('purpose', '')} {data.get('name', '')}"
                    if check_injection(user_input):
                        st.error("🚨 SECURITY ALERT: Prompt Injection Detected!")
                        st.error("The 'Guardian' layer blocked this request.")
                        st.stop()
                    else:
                        st.success("✅ Security Check Passed")
                        st.session_state["security_checked"] = True
                        st.rerun() # Rerun to proceed after security check

            if st.session_state.get("security_checked"):
                st.divider()
                st.subheader("🕵️ Agent Reasoning Trace")
                
                # Initialize Runner
                @st.cache_resource
                def get_runner_analysis():
                    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")
                    
                runner_analysis = get_runner_analysis()
                
                # Helper to execute agent run step
                async def run_step(prompt_text):
                    # Get or Create Session - FORCE NEW SESSION for Analysis to avoid Intake noise
                    if "analysis_session_id" not in st.session_state:
                        session = await runner_analysis.session_service.create_session(user_id="demo_user", app_name="loan_agent")
                        st.session_state["analysis_session_id"] = session.id
                    else:
                        session = await runner_analysis.session_service.get_session(st.session_state["analysis_session_id"])
                    
                    print(f"DEBUG: Running agent with prompt: {prompt_text[:50]}...")
                    async for event in runner_analysis.run_async(
                        session_id=session.id,
                        user_id="demo_user",
                        new_message=UserContent(parts=[Part(text=prompt_text)])
                    ):
                        yield event

                # Initialize events list
                if "trace_events" not in st.session_state:
                    st.session_state["trace_events"] = []

                async def execute_run(status_container, input_text):
                    try:
                        async for event in run_step(input_text):
                            msg = None
                            # Handle Agent Message
                            if hasattr(event, "content") and event.content:
                                if hasattr(event.content, "parts"):
                                    text_parts = []
                                    for p in event.content.parts:
                                        if hasattr(p, "text") and p.text:
                                            text_parts.append(p.text)
                                    if text_parts:
                                        full_text = "".join(text_parts)
                                        msg = ("agent", full_text)
                                        status_container.markdown(f"🤖 **Agent**: {full_text}")
                                        # Append to Chat History too!
                                        st.session_state["messages"].append({"role": "assistant", "content": full_text})
                                        
                            # Handle Tool Calls
                            elif hasattr(event, "tool_calls") and event.tool_calls:
                                for tc in event.tool_calls:
                                    if hasattr(tc, "function_calls"):
                                        for fc in tc.function_calls:
                                            msg = ("tool", f"🛠️ Calling Tool: `{fc.name}`")
                                            st.session_state["trace_events"].append(msg)
                                            status_container.write(msg[1])
                                            status_container.update(label=f"Executing {fc.name}...", state="running")
                                            render_audit_log(log_container)
                                            msg = None # Handled

                            if msg:
                                st.session_state["trace_events"].append(msg)
                                
                        status_container.update(label="✅ Update Complete. Agent is waiting.", state="complete", expanded=True)
                        
                    except Exception as e:
                        st.error(f"Agent Error: {e}")
                        status_container.update(label="❌ Error detected", state="error")
                        import traceback
                        traceback.print_exc()

                # 1. Initial Run (with Spinner/Status)
                if "agent_started" not in st.session_state:
                    initial_prompt = (
                        f"Review Loan Application for {data['name']} (ID: {data['applicant_id']}). "
                        f"Req: ${data['amount']:,} for {data['purpose']}. "
                        f"Stated Income: ${data['income']:,}, Employer: {data['employer']}."
                    )
                    with st.status("🤖 Agent is starting analysis...", expanded=True) as status:
                        asyncio.run(execute_run(status, initial_prompt))
                    st.session_state["agent_started"] = True
                    st.rerun()

                # Step Logic & Event Access
                events = st.session_state.get("trace_events", [])
                if "trace_index" not in st.session_state:
                    st.session_state["trace_index"] = 0
                    
                limit = st.session_state["trace_index"] + 1 if step_through else len(events)

                # 2. HITL: Reply to Agent
                # Only show input if trace is fully revealed or Step-Through is off
                if not step_through or limit >= len(events):
                    if reply := st.chat_input("Reply to agent..."):
                         with st.chat_message("user"):
                             st.write(reply)
                         st.session_state["messages"].append({"role": "user", "content": reply})
                         
                         with st.status("🤖 Agent is processing reply...", expanded=True) as status:
                              asyncio.run(execute_run(status, reply))
                         st.rerun()
                else:
                    # Show disabled input or message? 
                    # st.chat_input cannot be disabled easily, but we can just NOT render it.
                    # Instead, show a helper message.
                    st.info("ℹ️ Reveal all events to enable reply.")
                     
                # Step-by-Step Trace Display
                if step_through:
                    st.info("ℹ️ Step-Through Mode Active: Click 'Next' to reveal the agent's actions one by one.")

                for i in range(limit):
                    if i < len(events):
                        kind, text = events[i]
                        if kind == "agent":
                            st.markdown(f"🤖 **Agent**: {text}")
                            if "Final Decision" in text:
                                if "APPROVE" in text: st.success("✅ Approved")
                                elif "DENY" in text: st.error("❌ Denied")
                                elif "ESCALATE" in text: st.warning("⚠️ Escalated")
                        elif kind == "tool":
                            st.caption(text)

                if step_through and limit < len(events):
                    if st.button("Reveal Next Event ➡️"):
                        st.session_state["trace_index"] += 1
                        st.rerun()
                # Check for generated Decision PDF
                if step_through and limit >= len(events) and len(events) > 0:
                    st.success("🏁 Trace Review Complete")
                    
                    # Look for PDF in data/decisions
                    # Filename format: decision_{applicant_id}_{timestamp}.pdf
                    # We need to find the latest one for this applicant
                    decisions_dir = os.path.join(BASE_DIR, "loan_approval_agent/data/decisions")
                    if os.path.exists(decisions_dir):
                        pdf_files = [f for f in os.listdir(decisions_dir) if f.endswith(".pdf") and (data.get("applicant_id") in f or "decision" in f)]
                        # Sort by modification time (newest first)
                        pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(decisions_dir, x)), reverse=True)
                        
                        if pdf_files:
                            latest_pdf = pdf_files[0]
                            pdf_path = os.path.join(decisions_dir, latest_pdf)
                            
                            st.divider()
                            st.subheader("📄 Decision Record (Compliance)")
                            st.success(f"Generated: `{latest_pdf}`")
                            
                            with open(pdf_path, "rb") as f:
                                pdf_bytes = f.read()
                                st.download_button(
                                    label="📥 Download Decision Record (PDF)",
                                    data=pdf_bytes,
                                    file_name=latest_pdf,
                                    mime="application/pdf"
                                )
                        else:
                            st.warning("No Decision PDF found for this applicant.")
