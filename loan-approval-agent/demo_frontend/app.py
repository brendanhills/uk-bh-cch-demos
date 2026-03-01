import streamlit as st
import json
import asyncio
import sys
import os
import uuid
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
# We don't cache the runner to avoid complex event loop binding issues
# between Streamlit reruns.
def get_runner():
    return InMemoryRunner(agent=loan_manager, app_name="loan_agent")

# --- PATHS & STATE ---
LOG_PATH = os.path.join(BASE_DIR, "loan_agent/data/audit_logs/events.jsonl")
DECISION_DIR = os.path.join(BASE_DIR, "data/decisions")
os.makedirs(DECISION_DIR, exist_ok=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    # Clear logs on startup
    if os.path.exists(LOG_PATH):
        open(LOG_PATH, 'w').close()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# --- SIDEBAR: DEMO CONTROL ---
st.sidebar.title("🛠️ Demo Control")
st.sidebar.caption("Presenter tools (Not part of the UI)")

if st.sidebar.button("🔄 Start New Scenario", use_container_width=True, type="primary"):
    st.session_state["messages"] = []
    st.session_state["session_id"] = str(uuid.uuid4())
    if os.path.exists(LOG_PATH):
        open(LOG_PATH, 'w').close()
    for f in os.listdir(DECISION_DIR):
        os.remove(os.path.join(DECISION_DIR, f))
    st.rerun()

st.sidebar.markdown("---")

# Mock Applicant Data
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
    """Renders the audit log into the placeholder."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            lines = f.readlines()
            # Show last 20 events in reverse order
            content = ""
            for line in reversed(lines[-20:]):
                try:
                    data = json.loads(line)
                    icon = "🔘"
                    evt = data["event_type"].upper()
                    if "INVESTIGATION" in evt or "CHECK" in evt: icon = "🔍"
                    if "POLICY" in evt or "DOC" in evt: icon = "📜"
                    if "DECISION" in evt: icon = "⚖️"
                    if "ERROR" in evt: icon = "❌"
                    if "DLP" in evt or "SECURITY" in evt: icon = "🛡️"
                    if "REGISTER" in evt: icon = "📝"
                    
                    # Manual markdown construction for the placeholder
                    content += f"**{icon} {data['event_type']}**\n\n"
                    content += f"Agent: {data['agent']} | {data['timestamp']}\n\n"
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
    
    # Ensure session exists
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
        # Refresh trace LIVE
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

# Decision Records Download
with c_audit_col:
    pdf_files = sorted([f for f in os.listdir(DECISION_DIR) if f.endswith(".pdf")], reverse=True)
    if pdf_files:
        st.markdown("### 📄 Generated Records")
        for pdf in pdf_files[:3]:
            with open(os.path.join(DECISION_DIR, pdf), "rb") as f:
                st.download_button(f"⬇️ {pdf}", f, file_name=pdf)
