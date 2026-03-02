from loan_agent.agent import loan_manager
import time

import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

async def run_chat():
    print("=== Loan Manager CLI Test ===")
    
    # Initialize Runner
    from loan_agent.agent import app
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(user_id="cli_user", app_name="loan_agent")
    
    user_input = (
        "Process a new loan application for Sarah Speed (ID: 900-00-1234). "
        "She wants $15,000 for Home Improvement. She earns $85,000/year at TechCorp."
    )
    
    print(f"User Input: {user_input}\n")
    print("Agent Thinking...\n")
    
    start_time = time.time()
    
    try:
        response_text = ""
        async for event in runner.run_async(
            session_id=session.id,
            user_id="cli_user",
            new_message=UserContent(parts=[Part.from_text(text=user_input)])
        ):
            if hasattr(event, "content") and event.content:
                parts = [p.text for p in event.content.parts if p.text]
                if parts:
                    chunk = "".join(parts)
                    print(chunk, end="", flush=True)
                    response_text += chunk
            
            if hasattr(event, "tool_calls") and event.tool_calls:
                 for tc in event.tool_calls:
                     for fc in tc.function_calls:
                         print(f"\n[Tool Call] {fc.name}({fc.args})")
        
        print(f"\n\nTime Taken: {time.time() - start_time:.2f}s")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_chat())
