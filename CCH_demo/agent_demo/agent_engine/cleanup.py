"""
Delete the deployed cch-demo agent from Agent Engine.

Usage:
    uv run agent_engine/cleanup.py
"""

import os

import vertexai
from dotenv import load_dotenv

# Try loading .env from project root first, then from app directory
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
app_env = os.path.join(os.path.dirname(__file__), "..", "app", ".env")
if os.path.exists(root_env):
    load_dotenv(root_env, override=True)
elif os.path.exists(app_env):
    load_dotenv(app_env, override=True)
else:
    raise FileNotFoundError(
        "No .env configuration file found! Please copy app/.env.example to .env and configure your environment variables."
    )

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")


def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    resource_name = open("agent_resource_name.txt").read().strip()
    print(f"Deleting agent: {resource_name}")

    agent = client.agent_engines.get(name=resource_name)
    agent.delete(force=True)
    print("Agent deleted successfully.")

    os.remove("agent_resource_name.txt")


if __name__ == "__main__":
    main()
