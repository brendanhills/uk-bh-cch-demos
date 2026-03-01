import streamlit as st
import json
import asyncio
import sys
import os
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# --- CONFIGURATION & PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

try:
    from loan_agent.agent import loan_manager
    from loan_agent import config
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
@st.cache_resource
def get_runner():
    # simplest working initialization
    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")

runner = get_runner()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None

# --- DIRECTORY MANAGEMENT ---
DECISION_DIR = os.path.join(BASE_DIR, "data/decisions")
LOG_PATH = os.path.join(BASE_DIR, "loan_agent/data/audit_logs/events.jsonl")
os.makedirs(DECISION_DIR, exist_ok=True)

# --- SIDEBAR: DEMO CONTROL & CONVENIENCE ---
st.sidebar.title("🛠️ Demo Control")
st.sidebar.caption("Presenter tools (Not part of the UI)")

# New Scenario Button
if st.sidebar.button("🔄 Start New Scenario", use_container_width=True, type="primary"):
    st.session_state["messages"] = []
    st.session_state["session_id"] = None
    # Clear logs for demo clarity
    if os.path.exists(LOG_PATH):
        open(LOG_PATH, 'w').close()
    # Clear decisions
    for f in os.listdir(DECISION_DIR):
        os.remove(os.path.join(DECISION_DIR, f))
    st.rerun()

st.sidebar.markdown("---")

# Mock Applicant Data for Copy/Paste
st.sidebar.subheader("📋 Applicant Profiles")
mock_data = {
    "Sarah Speed (Approve)": "Hi, I'm Sarah Speed.\n\nSSN 900-00-1234. I earn $59,758\nI work at City Hospital.\n$20,000\ndebt consolidation.",
    "Sarah Speed (Decline)": "Hi, I'm Sarah Speed.\n\nSSN 900-00-1234.\nI'd like to increase my loan request to $50,000 for a luxury home improvement project.",
    "Gary Escalate": "Hi, I'm Gary Escalate.\n\nSSN 900-00-3456. I earn $60,000\nI work at Medianville Manufacturing.\n$15,000\nbusiness purchase.",
    "Jane Fraud": "Hi, I'm Jane Fraud.\n\nSSN 900-00-9999.\nI want a $5,000 loan.\nI don't currently have an employer."
}

for name, prompt in mock_data.items():
    with st.sidebar.expander(f"👤 {name}"):
        st.code(prompt, language="text")

# Simulation Settings
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Settings")
latency_mode = st.sidebar.radio("Latency:", ["TESTING", "REALISTIC"], index=0)
config.LATENCY_MODE = latency_mode

# --- LAYOUT: MAIN UI vs REASONING TRACE ---
c_main, c_trace = st.columns([0.65, 0.35], gap="large")

# Helper to render the live trace
def render_live_trace(container):
    with container:
        st.subheader("🕵️ Reasoning Trace")
        st.caption("Live agentic reasoning and tool execution")
        trace_box = st.container(height=600)
        with trace_box:
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, "r") as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        try:
                            data = json.loads(line)
                            icon = "🔘"
                            if "INVESTIGATION" in data["event_type"]: icon = "🔍"
                            if "POLICY" in data["event_type"]: icon = "📜"
                            if "DECISION" in data["event_type"]: icon = "⚖️"
                            if "ERROR" in data["event_type"]: icon = "❌"
                            
                            st.markdown(f"**{icon} {data['event_type']}**")
                            st.caption(f"Agent: {data['agent']}")
                            with st.expander("View Payload"):
                                st.json(data["details"])
                            st.markdown("---")
                        except:
                            pass
            else:
                st.info("Waiting for agent activity...")

with c_main:
    st.title("💰 FastLoan Portal")
    st.caption("Apply for your personal loan in seconds.")

    # Display Chat History
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- AUTO-GREETING ---
    if not st.session_state["messages"]:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if not st.session_state["session_id"]:
                session = loop.run_until_complete(runner.session_service.create_session(user_id="demo_user", app_name=runner.app_name))
                st.session_state["session_id"] = session.id

            async def get_greeting():
                full_resp = ""
                user_content = UserContent(parts=[Part(text="Hello! I am a new customer.")])
                async for event in runner.run_async(
                    user_id="demo_user",
                    session_id=st.session_state["session_id"],
                    new_message=user_content
                ):
                    # Refresh trace on every event for "live" feel
                    render_live_trace(c_trace)
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                full_resp += part.text
                                response_placeholder.markdown(full_resp + "▌")
                response_placeholder.markdown(full_resp)
                return full_resp

            greeting = loop.run_until_complete(get_greeting())
            st.session_state["messages"].append({"role": "assistant", "content": greeting})
            st.rerun()

    # Chat Input
    if prompt_text := st.chat_input("Tell us about your loan request..."):
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        with st.chat_message("user"):
            st.markdown(prompt_text)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            if not st.session_state["session_id"]:
                session = loop.run_until_complete(runner.session_service.create_session(user_id="demo_user", app_name=runner.app_name))
                st.session_state["session_id"] = session.id

            async def run_chat():
                full_resp = ""
                user_content = UserContent(parts=[Part(text=prompt_text)])
                async for event in runner.run_async(
                    user_id="demo_user",
                    session_id=st.session_state["session_id"],
                    new_message=user_content
                ):
                    # Refresh trace on every event for "live" feel
                    render_live_trace(c_trace)
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                full_resp += part.text
                                response_placeholder.markdown(full_resp + "▌")
                response_placeholder.markdown(full_resp)
                return full_resp

            final_response = loop.run_until_complete(run_chat())
            st.session_state["messages"].append({"role": "assistant", "content": final_response})
            st.rerun()

# Initial/Static trace render
render_live_trace(c_trace)

# Decision Records Download (Bottom of trace)
with c_trace:
    pdf_files = sorted([f for f in os.listdir(DECISION_DIR) if f.endswith(".pdf")], reverse=True)
    if pdf_files:
        st.markdown("### 📄 Generated Records")
        for pdf in pdf_files[:3]:
            st.download_button(f"⬇️ {pdf}", open(os.path.join(DECISION_DIR, pdf), "rb"), file_name=pdf)
