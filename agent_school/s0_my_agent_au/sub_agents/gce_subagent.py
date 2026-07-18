from google.adk.agents.llm_agent import Agent

def warn_capacity() -> str:
    """warns the user of a capacity contstraint"""
    return "capacity is constrained"

gce_subagent = Agent(
    model='gemini-2.5-flash',
    name='gce_subagent',
    description='A helpful assistant for user questions about GCP Compute Engine (GCE)',
    instruction=
    '''Answer user questions to the best of your knowledge for questions related to Google Cloud Compute (GCE)
      only.  Before answering any question, call the tool `warn_capacity` and prepend the answer
    ''',
    tools=[warn_capacity],

)
