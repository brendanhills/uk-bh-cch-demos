# main.py

import asyncio
import os
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai.types import Content, Part
from agents import root_agent

# --- Configuration ---
SESSIONS_DIR = Path(os.path.expanduser("~")) / ".adk" / "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
DB_FILE = SESSIONS_DIR / "adk_cli_sessions.db"
SESSION_URL = f"sqlite+aiosqlite:///{DB_FILE}"
MY_USER_ID = "local_cli_user_001"
MY_SESSION_ID = f"{MY_USER_ID}_cli_session"


async def main():
    print("🤖 Initializing Personalized Trip Planner CLI...")
    print(f"🗄️  Session database is at: {DB_FILE}")
    print("--------------------------------------------------")

    session_service = DatabaseSessionService(db_url=SESSION_URL)
    session = await session_service.get_session(
        app_name=root_agent.name, user_id=MY_USER_ID, session_id=MY_SESSION_ID
    )
    if session is None:
        print(f"No existing session found. Creating a new one: {MY_SESSION_ID}")
        session = await session_service.create_session(
            app_name=root_agent.name, user_id=MY_USER_ID, session_id=MY_SESSION_ID
        )
    print(f"✅ Session '{session.id}' is ready for user '{session.user_id}'.")

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=root_agent.name
    )

    while True:
        try:
            query = input("You: ")
            if query.lower() in ["quit", "exit"]:
                print("🤖 Goodbye!")
                break
            
            print("Agent: ", end="", flush=True)

            # --- START: Updated Event Handling Loop ---
            # This new loop is more robust. It iterates through all parts of each event
            # and explicitly handles each type (text, tool results, etc.),
            # preventing the warning about non-text parts.
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=Content(parts=[Part(text=query)], role="user")
            ):
                if not event.content:
                    continue  # Skip events that have no content

                for part in event.content.parts:
                    # Case 1: The model sends a text chunk for the user.
                    # We check if part.text exists and is not empty.
                    if hasattr(part, "text") and part.text:
                        # Print it immediately to create a streaming effect
                        print(part.text, end="", flush=True)

                    # Case 2: A tool finished running. We print its result for debugging.
                    # The ADK sends tool results back to the model as a "user" authored event.
                    elif event.author == "user" and hasattr(part, "function_response"):
                        tool_name = part.function_response.name
                        tool_result = part.function_response.response
                        
                        # Print debug info on a new line to avoid mixing it with agent output
                        print(f"\n\n[DEBUG] Tool '{tool_name}' returned: {tool_result}\n")
                        
                        # Re-print the "Agent:" prompt to show it's processing the tool result
                        print("Agent: ", end="", flush=True)
            
            # Add a final newline for clean formatting before the next user prompt
            print("\n")
            # --- END: Updated Event Handling Loop ---

        except (KeyboardInterrupt, EOFError):
            print("\n🤖 Goodbye!")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down.")