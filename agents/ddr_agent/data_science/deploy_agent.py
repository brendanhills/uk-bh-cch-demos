import os
import requests

def register_agent():
    url = 'https://discoveryengine.googleapis.com/v1alpha/projects/uk-bh-experiments-argolis/locations/global/collections/default_collection/engines/bh-test-as_1744715457558/assistants/default_assistant/agents'

    payload = {
        'displayName': 'Data Science Agent 2', 
        'description': 'v2 of a Data Science Agent', 
        'adk_agent_definition': {
            'tool_settings': {
                'tool_description': 'Use this tool to analyse sales data for stickers'
            }, 
            'provisioned_reasoning_engine': {
                    'reasoning_engine': 'projects/uk-bh-experiments-argolis/locations/global/reasoningEngines/2672684068704878592'
            }
        }
    }

    stream = os.popen("gcloud auth print-access-token")
    token = stream.read().strip()
    print(f"Token: {token}")
    headers = {'content-type': 'application/json',  'Authorization': f'Bearer {token}', 'X-Goog-User-Project': 'uk-bh-experiments-argolis'}

    r = requests.post(url, data=payload, headers=headers)

    #print(f"URL = {r.url}")
    #print(r.status_code)
    print(r.headers)

def view_agent(agent_resource_name):

    url = f'https://discoveryengine.googleapis.com/v1alpha/{agent_resource_name}'

    stream = os.popen("gcloud auth print-access-token")
    token = stream.read().strip()
    #print(f"Token: {token}")
    headers = {'content-type': 'application/json',  'Authorization': f'Bearer {token}', 'X-Goog-User-Project': 'uk-bh-experiments-argolis'}

    r = requests.get(url, headers=headers)

    print(f"URL = {r.url}")
    print(r.status_code)
    print(r.headers)
    print(r.json())

def main():
    name = "projects/376231489344/locations/global/collections/default_collection/engines/bh-test-as_1744715457558/assistants/default_assistant/agents/5993313733808312602"
    view_agent(name)
    #register_agent()

if __name__ == "__main__":
    main()
