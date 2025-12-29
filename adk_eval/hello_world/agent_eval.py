import asyncio
from google.adk.evaluation import AgentEvaluator
from hello_world.agent import root_agent

## run adk eval hello_world/  --config_file_path eval_config_no_metrics.json --print_detailed_results --log_level=DEBUG^C

AGENT_MODULE_PATH="hello_world"
AGENT_PATH="hello_world.agent.root_agent"
EVAL_SET_PATH="set_with_conversation_scenarios.evalset.json"
NUM_RUNS=1
AGENT_NAME="hello_world_agent"
INITIAL_SESSION_PATH="eval_config_no_metrics.json"


async def run_evaluation():
    result = await AgentEvaluator.evaluate(AGENT_PATH, EVAL_SET_PATH, NUM_RUNS, AGENT_NAME, INITIAL_SESSION_PATH)
    print(f"{result=}")

async def main():
   print(await run_evaluation())
   await run_evaluation()

if __name__ == '__main__':
   asyncio.run(main())
