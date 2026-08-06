# main_trip.py
import asyncio
import os
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# Import the new trip agent
from trip_agent import root_agent

async def main():
    print("🤖 Initializing Trip Planner Agent CLI...")
    print("--------------------------------------------------")

    # Using a simple temporary session for this example
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=root_agent.name, user_id="cli_user", session_id="trip_session"
    )

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

            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=Content(parts=[Part(text=query)], role="user")
            ):
                if event.content:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            print(part.text, end="", flush=True)

            print("\n")

        except (KeyboardInterrupt, EOFError):
            print("\n🤖 Goodbye!")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down.")