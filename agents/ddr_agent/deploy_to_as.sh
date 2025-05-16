curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: uk-bh-experiments-argolis" \
"https://discoveryengine.googleapis.com/v1alpha/projects/uk-bh-experiments-argolis/locations/global/collections/default_collection/engines/bh-test-as_1744715457558/assistants/default_assistant/agents" \
-d '{
    "displayName": "Data Science Agent 3",
    "description": "v3 of a Data Science Agent",
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "Use this tool to analyse sales data for stickers"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine":
            "projects/uk-bh-experiments-argolis/locations/global/reasoningEngines/2672684068704878592"
        },
    }
}'