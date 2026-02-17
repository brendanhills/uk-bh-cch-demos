import streamlit as st
import json
import asyncio
import sys
import os
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# Ensure we are in the project root
sys.path.append(os.getcwd())

# Import config to load environment variables
from loan_approval_agent import config
from loan_approval_agent.agent import loan_manager

st.set_page_config(page_title="Fintech Loan Agent", layout="wide")

st.title("🤖 Fintech Loan Approval Agent")
st.markdown("### AI-Powered Underwriting Demo")

# Mock Data for Demo
applicants = {
    "12345": {"name": "John Doe", "stated_income": 50000, "employer": "Tech Corp", "credit_score": 720},
    "12346": {"name": "Alice Smith", "stated_income": 80000, "employer": "Consulting Inc", "credit_score": 580},
    "12347": {"name": "Bob Johnson", "stated_income": 120000, "employer": "Finance LLP", "credit_score": 800},
    "12348": {"name": "Gary Gray", "stated_income": 60000, "employer": "Medianville Manufacturing", "credit_score": 620},
    "12349": {"name": "Jane Doe", "stated_income": 0, "employer": "", "credit_score": 700},
}

scenarios = [
    {"name": "Happy Path (Approval)", "applicant_id": "12345", "loan_amount": 10000, "purpose": "Home Improvement"},
    {"name": "High Debt (Denial)", "applicant_id": "12346", "loan_amount": 50000, "purpose": "Business"},
    {"name": "Complex Case (Manual Review)", "applicant_id": "12347", "loan_amount": 200000, "purpose": "Education"},
    {"name": "Borderline Credit (Escalation)", "applicant_id": "12348", "loan_amount": 15000, "purpose": "Debt Consolidation"},
    {"name": "Missing Info (Q&A)", "applicant_id": "12349", "loan_amount": 5000, "purpose": "Personal"},
]

# Sidebar: Demo Controller
with st.sidebar:
    st.header("🎮 Demo Controller")
    st.info("Select a scenario below to see details for the demo.")
    
    # Scenario Selector
    scenario_options = {s["name"]: s for s in scenarios}
    selected_scenario_name = st.selectbox(
        "Select Scenario",
        ["Choose..."] + list(scenario_options.keys())
    )
    
    if selected_scenario_name != "Choose...":
        s = scenario_options[selected_scenario_name]
        a = applicants.get(s["applicant_id"])
        
        st.markdown("### 📋 Reference Data")
        st.markdown("Copy these values into the form:")
        
        st.text_input("Applicant ID", value=s["applicant_id"], key="ref_id", disabled=False)
        st.text_input("Name", value=a["name"], key="ref_name", disabled=False)
        st.text_input("Income", value=str(a["stated_income"]), key="ref_income", disabled=False)
        st.text_input("Employer", value=a["employer"], key="ref_employer", disabled=False)
        st.text_input("Loan Amount", value=str(s["loan_amount"]), key="ref_amount", disabled=False)
        st.text_input("Purpose", value=s["purpose"], key="ref_purpose", disabled=False)
        
        st.divider()
        if st.button("⚡ Quick Fill (Skip Wizard)"):
            st.session_state["form_data"] = {
                "applicant_id": s["applicant_id"],
                "name": a["name"],
                "income": a["stated_income"],
                "employer": a["employer"],
                "amount": s["loan_amount"],
                "purpose": s["purpose"]
            }
            st.session_state["wizard_step"] = 4
            st.rerun()

    st.divider()
    # Latency Toggle
    latency_mode = st.radio(
        "Latency Mode",
        ["REALISTIC", "TESTING"],
        help="REALISTIC: Simulates API delays (e.g. 30s).\nTESTING: Instant responses."
    )
    config.LATENCY_MODE = latency_mode
    
# Main Content Area
        
        # UI Layout
# Initialize Session State
if "wizard_step" not in st.session_state:
    st.session_state["wizard_step"] = 1
if "form_data" not in st.session_state:
    st.session_state["form_data"] = {}

# Wizard Flow
st.markdown("### 📝 New Loan Application")

# Progress Bar
progress = (st.session_state["wizard_step"] - 1) / 3
st.progress(progress)

# Step 1: Personal Info
if st.session_state["wizard_step"] == 1:
    st.subheader("Step 1: Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        # We default to values if they exist in form_data (from Quick Fill)
        def_id = st.session_state["form_data"].get("applicant_id", "")
        applicant_id = st.text_input("Applicant ID", value=def_id, help="Unique ID linked to credit bureau.")
        
    with col2:
        def_name = st.session_state["form_data"].get("name", "")
        name = st.text_input("Full Name", value=def_name)
        
    if st.button("Next ➡️"):
        if not applicant_id or not name:
            st.error("Please fill in all fields.")
        else:
            st.session_state["form_data"]["applicant_id"] = applicant_id
            st.session_state["form_data"]["name"] = name
            st.session_state["wizard_step"] = 2
            st.rerun()

# Step 2: Financials
elif st.session_state["wizard_step"] == 2:
    st.subheader("Step 2: Financial Details")
    
    col1, col2 = st.columns(2)
    with col1:
        def_income = st.session_state["form_data"].get("income", 50000)
        income = st.number_input("Annual Stated Income ($)", value=def_income, step=1000)
        
    with col2:
        def_employer = st.session_state["form_data"].get("employer", "")
        employer = st.text_input("Current Employer", value=def_employer)
        
    st.markdown("#### 📂 Supporting Documents")
    uploaded_files = st.file_uploader(
        "Upload Payslips or Bank Statements (PDF)", 
        type=["pdf"], 
        accept_multiple_files=True
    )
        
    col_nav1, col_nav2 = st.columns([1, 1])
    if col_nav1.button("⬅️ Back"):
        st.session_state["wizard_step"] = 1
        st.rerun()
    if col_nav2.button("Next ➡️"):
        st.session_state["form_data"]["income"] = income
        st.session_state["form_data"]["employer"] = employer
        
        # Save files
        if uploaded_files:
            file_paths = []
            upload_dir = "artifacts/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            for uploaded_file in uploaded_files:
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
            st.session_state["form_data"]["document_paths"] = file_paths
            
        st.session_state["wizard_step"] = 3
        st.rerun()

# Step 3: Loan Details
elif st.session_state["wizard_step"] == 3:
    st.subheader("Step 3: Loan Request")
    
    col1, col2 = st.columns(2)
    with col1:
        def_amount = st.session_state["form_data"].get("amount", 10000)
        amount = st.number_input("Requested Amount ($)", value=def_amount, step=1000)
        
    with col2:
        def_purpose = st.session_state["form_data"].get("purpose", "Debt Consolidation")
        purpose = st.selectbox("Loan Purpose", 
                             ["Debt Consolidation", "Home Improvement", "Business", "Education", "Other"],
                             index=["Debt Consolidation", "Home Improvement", "Business", "Education", "Other"].index(def_purpose) if def_purpose in ["Debt Consolidation", "Home Improvement", "Business", "Education", "Other"] else 0)
        
    col_nav1, col_nav2 = st.columns([1, 1])
    if col_nav1.button("⬅️ Back"):
        st.session_state["wizard_step"] = 2
        st.rerun()
    if col_nav2.button("Next ➡️"):
        st.session_state["form_data"]["amount"] = amount
        st.session_state["form_data"]["purpose"] = purpose
        st.session_state["wizard_step"] = 4
        st.rerun()

# Step 4: Review & Submit
elif st.session_state["wizard_step"] == 4:
    st.subheader("Step 4: Review Application")
    
    data = st.session_state["form_data"]
    
    st.info("Please review the details below before submitting.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Applicant", data.get("name"))
    c1.caption(f"ID: {data.get('applicant_id')}")
    
    c2.metric("Income", f"${data.get('income'):,}")
    c2.caption(f"Employer: {data.get('employer')}")
    
    c3.metric("Loan Amount", f"${data.get('amount'):,}")
    c3.caption(f"Purpose: {data.get('purpose')}")
    
    st.divider()
    
    col_nav1, col_nav2 = st.columns([1, 1])
    if col_nav1.button("⬅️ Back"):
        st.session_state["wizard_step"] = 3
        st.rerun()
        
    if col_nav2.button("🚀 Submit Application", type="primary"):
        # Trigger Agent Logic
        st.session_state["submitted"] = True
        
    
    if st.session_state.get("submitted"):
        st.divider()
        col_res1, col_res2 = st.columns([3, 2])
        
        with col_res1:
            st.subheader("🕵️ Agent Reasoning Trace")

    if st.session_state.get("submitted"):
        st.divider()
        col_res1, col_res2 = st.columns([3, 2])
        
        with col_res1:
            st.subheader("🕵️ Agent Reasoning Trace")
            
            # Retrieve cached Runner instance
            @st.cache_resource
            def get_global_runner():
                return InMemoryRunner(agent=loan_manager, app_name="agents")

            if "agent_runner" not in st.session_state:
                st.session_state["agent_runner"] = get_global_runner()
                st.session_state["agent_session_id"] = None

            # Helper to run agent (initial or follow-up)
            async def run_agent_gen(user_msg: str = None):
                runner = st.session_state["agent_runner"]
                
                # Create session if not exists
                if not st.session_state["agent_session_id"]:
                    session = await runner.session_service.create_session(
                        app_name=runner.app_name, user_id="demo_user"
                    )
                    st.session_state["agent_session_id"] = session.id
                    
                    # Initial prompt
                    initial_input = (
                        f"Begin review for applicant_id: {data['applicant_id']}. "
                        f"Requested Loan Amount: ${data['amount']:,}. "
                        f"Loan Purpose: {data['purpose']}."
                    )
                    
                    if "document_paths" in data and data["document_paths"]:
                        initial_input += f"\nThe applicant has provided supporting documents: {', '.join(data['document_paths'])}. Please analyze these to verify income and employment."

                    content = UserContent(parts=[Part(text=initial_input)])
                        
                    yield ("system", f"📥 **System**: Received Application for {data['name']}")
                else:
                    # Follow-up
                    content = UserContent(parts=[Part(text=user_msg)])
                    yield ("user", f"👤 **User**: {user_msg}")

                async for event in runner.run_async(
                    user_id="demo_user",
                    session_id=st.session_state["agent_session_id"],
                    new_message=content,
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                yield ("agent", part.text)
                                
                    elif hasattr(event, 'tool_calls') and event.tool_calls:
                        for tool_call in event.tool_calls:
                            fn_name = tool_call.function_calls[0].name
                            if "agent" in fn_name:
                                 yield ("handoff", f"🔄 **Handoff**: Delegating to `{fn_name}`")
                            else:
                                 yield ("tool", f"🛠️ **Tool Call**: `{fn_name}`")
                
                # We don't yield complete here because it might continue

            # Initialize Trace Events if new
            if "trace_events" not in st.session_state:
                 st.session_state["trace_events"] = []
                 # Run initial automatically
                 async def run_initial():
                     events = []
                     async for e in run_agent_gen():
                         events.append(e)
                     return events
                 
                 with st.spinner("Processing Application..."):
                     new_events = asyncio.run(run_initial())
                     st.session_state["trace_events"].extend(new_events)
                     if step_through:
                         st.session_state["trace_index"] = 0
                     else:
                         st.session_state["trace_index"] = len(st.session_state["trace_events"]) - 1

            # Render Events (Step-Through or Full)
            events = st.session_state["trace_events"]
            limit = st.session_state["trace_index"] + 1 if step_through else len(events)
            
            with st.status("Execution Trace", expanded=True) as status:
                final_decision_found = False
                question_found = None
                
                for i in range(limit):
                    if i < len(events):
                        tipo, text = events[i]
                        if tipo == "agent":
                            status.write(f"🤖 **Agent**: {text}")
                            if "Question:" in text:
                                question_found = text
                            if "Final Decision:" in text or "ESCALATED" in text:
                                final_decision_found = True
                        elif tipo == "user":
                            status.write(text)
                        elif tipo == "handoff":
                            status.write(text)
                        elif tipo == "tool":
                             status.write(text)
                        elif tipo == "system":
                            status.write(text)
                
                if step_through and limit < len(events):
                    status.update(label=f"Paused at Step {limit}/{len(events)}", state="running")
                elif final_decision_found:
                    status.update(label="✅ Analysis Complete", state="complete")
                elif question_found:
                    status.update(label="❓ Additional Info Required", state="running")

            # Step-Through Controls
            if step_through and limit < len(events):
                if st.button("Next Step ➡️", key=f"next_{limit}"):
                    st.session_state["trace_index"] += 1
                    st.rerun()

            # Q&A / Final Decision UI
            # Only show if we are at the end of current events
            if not step_through or limit == len(events):
                # Check for Question
                last_agent_msg = next((e[1] for e in reversed(events) if e[0] == "agent"), "")
                
                if "Question:" in last_agent_msg and "Final Decision:" not in last_agent_msg:
                    st.divider()
                    st.info("The agent has a question for you.")
                    q_text = last_agent_msg.split("Question:")[-1].strip()
                    st.markdown(f"**❓ Question**: {q_text}")
                    
                    with st.form("qa_form"):
                        answer = st.text_input("Your Answer")
                        if st.form_submit_button("Submit Answer"):
                            # Run Agent with Answer
                            async def run_reply():
                                new_evs = []
                                async for e in run_agent_gen(answer):
                                    new_evs.append(e)
                                return new_evs
                                
                            with st.spinner("Submitting Answer..."):
                                reply_events = asyncio.run(run_reply())
                                st.session_state["trace_events"].extend(reply_events)
                                if step_through:
                                    # Don't auto advance index, let user step? 
                                    # Or just let it flow until next pause? 
                                    # Simplest: Just append and let loop handle it.
                                    pass
                                else:
                                    st.session_state["trace_index"] = len(st.session_state["trace_events"]) - 1
                            st.rerun()
                            
                # Check for Final Decision
                full_text = "".join([e[1] for e in events if e[0] == "agent"])
                start_marker = "Final Decision:"
                if start_marker in full_text:
                    decision_text = full_text.split(start_marker)[-1].strip()
                    st.markdown("### 📝 Final Decision")
                    if "ESCALATE" in decision_text.upper():
                        st.warning(f"⚠️ **Escalated for Human Review**")
                        st.info(f"Reason: {decision_text}")
                    elif "APPROVE" in decision_text.upper():
                        st.success(f"✅ **Approved**")
                        st.markdown(f"**Details**: {decision_text}")
                    elif "DENY" in decision_text.upper():
                        st.error(f"❌ **Denied**")
                        st.markdown(f"**Reason**: {decision_text}")
                    else:
                        st.markdown(f"**{start_marker}** {decision_text}")
