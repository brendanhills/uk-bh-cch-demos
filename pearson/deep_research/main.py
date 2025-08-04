import argparse
import os
import json
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "global")  # Default to "global" if not set
APP_ID = os.getenv("APP_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
DEFAULT_QUERY = os.getenv("DEFAULT_QUERY", "how do i use bigquery")  # Default query
AGENT_ID = os.getenv("AGENT_ID")


def get_token():
#   raw_token = ! gcloud auth print-access-token
#   token = f'Bearer {raw_token[0]}'

    creds, project = google.auth.default()

    # creds.valid is False, and creds.token is None
    # Need to refresh credentials to populate those

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)

    # Now you can use creds.token
    token = f'Bearer {creds.token}'
    return token

def build_research_URL(PROJECT_ID, LOCATION, APP_ID, ASSISTANT_ID):
  url=   URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{APP_ID}/assistants/{ASSISTANT_ID}:streamAssist"
  return url



def get_plan(query, token, project_id, location, app_id, assistant_id, agent_id):
    url = build_research_URL(project_id, location, app_id, assistant_id)

    plan_response = requests.post(
    (url),
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
        'X-Goog-User-Project': project_id
    },
    json={
       'query': {
          'text': query,
          },
        'answerGenerationMode': 'research',
        "assistSkippingMode": "REQUEST_ASSIST",
        'googleSearchGroundingEnabled': True,
        "agentsSpec": {
            "agentSpecs": {
                "agentId": agent_id
                }
            },
        },
    )
    session_id = plan_response.json()[0]['sessionInfo']['session']
    reply = plan_response.json()[0]['answer']['replies'][0]['groundedContent']['content']['text']
    plan = plan_response.json()[0]['answer']['replies'][1]['groundedContent']['content']['text']

    return session_id, reply, plan


def get_research(session_id, token, project_id, location, app_id, assistant_id, agent_id, stream=False):
    url = build_research_URL(project_id, location, app_id, assistant_id)
    research_response = requests.post(
        (
            url
        ),
      headers = {
          'Authorization': token,
          'Content-Type': 'application/json',
          'X-Goog-User-Project': project_id
      },
      json={
        'query': {
            'text': "Start Research",
        },
        "session": session_id,
        "assistSkippingMode": "REQUEST_ASSIST",
        "agentsSpec": {
          "agentSpecs": {
            "agentId": agent_id
          }
        },
        'answerGenerationMode': 'research',
        'googleSearchGroundingEnabled': True
      },
      stream=stream
    )
    if stream:
        research_response_text = ""
        for line in research_response.iter_lines(decode_unicode=True):
            if line:
                respose_line = line
                print(respose_line)
                #print(line.json()[0]['answer']['replies'][1]['groundedContent']['content']['text'])
                research_response_text += line
        research_response_json = json.loads(research_response_text)
    else:
        research_response_json = research_response.json()

    return research_response_json

def main():
    """
    Main function to execute the deep research process.
    """
    if not all([PROJECT_ID, LOCATION, APP_ID, ASSISTANT_ID, AGENT_ID, DEFAULT_QUERY]):
        print("Error: One or more environment variables are not set.")
        print(
            "Please create a .env file with PROJECT_ID, LOCATION, APP_ID, ASSISTANT_ID, DEFAULT_QUERY and AGENT_ID."
        )
        return

    parser = argparse.ArgumentParser()
    parser.parse_args()
    parser.add_argument("--query", type=str, help="query")
    args = parser.parse_args()
    if args.query is None:
        QUERY = DEFAULT_QUERY
    else:
        QUERY = args.query


    print("Starting deep research...")
    try:
        token = get_token()
        print("Successfully obtained auth token.")

        url = build_research_URL(PROJECT_ID, LOCATION, APP_ID, ASSISTANT_ID)
        print(f"Research URL: {url}")

        print(f"\n--- Getting plan for query: '{QUERY}' ---")
        session_id, reply, plan = get_plan(QUERY, token, PROJECT_ID,  LOCATION, APP_ID, ASSISTANT_ID, AGENT_ID,)
        print(f"Session ID: {session_id}")
        print(f"Initial Reply: {reply}")
        print(f"Research Plan:\n{plan}")

        print("\n--- Starting research (streaming) ---")
        research_result = get_research(session_id, token, PROJECT_ID, LOCATION, APP_ID, ASSISTANT_ID, AGENT_ID, stream=True)
        print("\n--- Research Result (parsed) ---")
        print(json.dumps(research_result, indent=2))

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response body: {http_err.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
