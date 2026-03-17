import vertexai
import asyncio
import json

engine_id = "projects/ge-hands-master26lon-53/locations/us-central1/reasoningEngines/3649568264146649088"
client = vertexai.Client(location="us-central1")
agent = client.agent_engines.get(name=engine_id)

async def test():
    try:
        # try async_stream_query first
        print("Trying async_stream_query...")
        async for event in agent.async_stream_query(message="Hello!", user_id="test"):
            print(event)
    except Exception as e:
        print("async_stream_query failed:", e)

    try:
        print("Trying query...")
        res = getattr(agent, "query")(message="Hello!", user_id="test")
        print(res)
    except Exception as e:
        print("query failed:", e)
        
asyncio.run(test())
