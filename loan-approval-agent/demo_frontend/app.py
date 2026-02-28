import streamlit as st
import json
import asyncio
import sys
import os
import shutil
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# --- CONFIGURATION & PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

try:
    from loan_agent.agent import loan_manager, app
    from loan_agent import config
    from loan_agent.utils import token_vault
except ImportError as e:
    st.error(f"Failed to import loan_agent: {e}. Ensure you are running from the project root.")
    st.stop()

# --- STREAMLIT UI SETUP ---
st.set_page_config(
    page_title="Loan Approval Demo",
    page_icon="💰",
    layout="wide"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "events" not in st.session_state:
    st.session_state["events"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None

# --- DIRECTORY MANAGEMENT ---
DECISION_DIR = os.path.join(BASE_DIR, "data/decisions")
os.makedirs(DECISION_DIR, exist_ok=True)

def clear_decisions():
    for f in os.listdir(DECISION_DIR):
        os.remove(os.path.join(DECISION_DIR, f))

# --- SIDEBAR: DEMO CONTROL & CONVENIENCE ---
st.sidebar.title("🛠️ Demo Control")
st.sidebar.caption("Presenter convenience tools (Not part of the UI)")
st.sidebar.markdown("---")

# Mock Applicant Data for Copy/Paste
st.sidebar.subheader("📋 Applicant Profiles")
st.sidebar.caption("Copy these values into the chat panel.")

mock_data = {
    "Sarah Speed (Approve)": {
        "prompt": "Hi, I'm Sarah Speed.\n\nSSN 900-00-1234. I earn $59,758\nI work at City Hospital.\n$20,000\ndebt consolidation."
    },
    "Sarah Speed (Decline)": {
        "prompt": "Hi, I'm Sarah Speed.\n\nSSN 900-00-1234.\nI'd like to increase my loan request to $50,000 for a luxury home improvement project."
    },
    "Gary Escalate": {
        "prompt": "Hi, I'm Gary Escalate.\n\nSSN 900-00-3456. I earn $60,000\nI work at Medianville Manufacturing.\n$15,000\nbusiness purchase."
    },
    "Jane Fraud": {
        "prompt": "Hi, I'm Jane Fraud.\n\nSSN 900-00-9999.\nI want a $5,000 loan.\nI don't currently have an employer."
    }
}

for name, data in mock_data.items():
    with st.sidebar.expander(f"👤 {name}"):
        st.code(data["prompt"], language="text")

# Simulation Settings
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Simulation Settings")
latency_mode = st.sidebar.radio("Latency:", ["TESTING", "REALISTIC"], index=0)
config.LATENCY_MODE = latency_mode

if st.sidebar.button("🗑️ Clear Decision Records"):
    clear_decisions()
    st.sidebar.success("Cleared!")

# --- MAIN: SIMULATED USER INTERFACE ---
c_main, c_audit = st.columns([0.65, 0.35], gap="large")

with c_main:
    st.title("💰 FastLoan Portal")
    st.caption("Apply for your personal loan in seconds.")

    # Display Chat History
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt_text := st.chat_input("Tell us about your loan request..."):
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        with st.chat_message("user"):
            st.markdown(prompt_text)

        # Run Agent
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            @st.cache_resource
            def get_runner():
                return InMemoryRunner(app=app)
            
            runner = get_runner()
            
            # Start session if not exists
            if not st.session_state["session_id"]:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                session = loop.run_until_complete(runner.session_service.create_session(user_id="demo_user", app_name="loan_agent"))
                st.session_state["session_id"] = session.id

            async def execute_run(input_text):
                user_content = UserContent(parts=[Part(text=input_text)])
                async for event in runner.run_async(
                    user_id="demo_user",
                    session_id=st.session_state["session_id"],
                    new_message=user_content
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                yield part.text

            async def stream_output(text_input):
                full_resp = ""
                async for chunk in execute_run(text_input):
                    full_resp += chunk
                    response_placeholder.markdown(full_resp + "▌")
                response_placeholder.markdown(full_resp)
                return full_resp

            full_response = asyncio.run(stream_output(prompt_text))
            st.session_state["messages"].append({"role": "assistant", "content": full_response})

    # Auto-Greeting Logic
    if not st.session_state["messages"]:
        # Setup session
        @st.cache_resource
        def get_runner_init():
            return InMemoryRunner(app=app)
        runner_init = get_runner_init()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session = loop.run_until_complete(runner_init.session_service.create_session(user_id="demo_user", app_name="loan_agent"))
        st.session_state["session_id"] = session.id

        async def execute_greeting():
            user_content = UserContent(parts=[Part(text="Hello! I am a new customer.")])
            async for event in runner_init.run_async(
                user_id="demo_user",
                session_id=st.session_state["session_id"],
                new_message=user_content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield part.text

        async def stream_greeting():
            full_resp = ""
            with st.chat_message("assistant"):
                ph = st.empty()
                async for chunk in execute_greeting():
                    full_resp += chunk
                    ph.markdown(full_resp + "▌")
                ph.markdown(full_resp)
            return full_resp

        greeting_text = asyncio.run(stream_greeting())
        st.session_state["messages"].append({"role": "assistant", "content": greeting_text})
        st.rerun()

# --- RIGHT: REAL-TIME REASONING TRACE (Audit Log) ---
with c_audit:
    st.subheader("🕵️ Reasoning Trace")
    st.caption("Live developer view of agent orchestration")
    
    # Audit log display
    audit_container = st.container(height=600)
    with audit_container:
        LOG_PATH = os.path.join(BASE_DIR, "loan_agent/data/audit_logs/events.jsonl")
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                lines = f.readlines()
                # Show last 20 events
                for line in reversed(lines[-20:]):
                    try:
                        data = json.loads(line)
                        icon = "🔍" if "INVESTIGATION" in data["event_type"] else "📜" if "POLICY" in data["event_type"] else "⚖️" if "DECISION" in data["event_type"] else "🔘"
                        st.markdown(f"**{icon} {data['event_type']}**")
                        st.caption(f"{data['timestamp']} | Agent: {data['agent']}")
                        with st.expander("View Internal Data"):
                            st.json(data["details"])
                        st.markdown("---")
                    except:
                        pass
        else:
            st.write("Waiting for agent activity...")

    # Decision Record Download
    pdf_files = sorted([f for f in os.listdir(DECISION_DIR) if f.endswith(".pdf")], reverse=True)
    if pdf_files:
        st.markdown("### 📄 Generated Records")
        for pdf in pdf_files[:3]:
            st.download_button(f"⬇️ {pdf}", open(os.path.join(DECISION_DIR, pdf), "rb"), file_name=pdf)

# --- FILE UPLOAD (OPTIONAL) ---
st.sidebar.markdown("---")
st.sidebar.subheader("📎 Document Upload")
uploaded_file = st.sidebar.file_uploader("Upload for Vision Analysis", type=["pdf", "png", "jpg"])
if uploaded_file:
    if st.sidebar.button("🔍 Analyze with Vision"):
        with st.spinner("Processing..."):
            from loan_agent.tools.doc_analyzer import analyze_paystub
            result = analyze_paystub(uploaded_file.getvalue())
            st.sidebar.json(result)
