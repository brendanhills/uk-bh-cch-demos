"""Telemetry and latency instrumentation wrappers for ADK sub-agents and tools."""

import time
import logging
from typing import Any, Dict, List
from google.adk.tools import AgentTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger("cch_agent.telemetry")
call_transcript_logger = logging.getLogger("call_transcripts")


class TimedAgentTool(AgentTool):
    """Subclass of ADK AgentTool that instruments sub-agent dispatch and execution with high-precision timestamp logging."""

    def __init__(
        self,
        agent: Any,
        skip_summarization: bool = True,
        *,
        include_plugins: bool = True,
        propagate_grounding_metadata: bool = False,
    ):
        super().__init__(
            agent=agent,
            skip_summarization=skip_summarization,
            include_plugins=include_plugins,
            propagate_grounding_metadata=propagate_grounding_metadata,
        )

    async def run_async(self, *, args: dict[str, Any], tool_context: ToolContext) -> Any:
        """Executes wrapped sub-agent while recording high-precision execution timestamps and latency."""
        start_counter = time.perf_counter()
        start_time = time.time()
        
        logger.info(f"[SUB_AGENT_DISPATCH_START] sub_agent={self.name} args={args}")
        call_transcript_logger.info(f"[SUB_AGENT_DISPATCH_START] sub_agent={self.name} args={args}")

        try:
            result = await super().run_async(args=args, tool_context=tool_context)
            elapsed_sec = time.perf_counter() - start_counter
            elapsed_ms = elapsed_sec * 1000.0

            log_msg = (
                f"[SUB_AGENT_DISPATCH_END] sub_agent={self.name} "
                f"duration_ms={elapsed_ms:.2f}ms ({(elapsed_sec):.3f}s) status=SUCCESS"
            )
            logger.info(log_msg)
            call_transcript_logger.info(log_msg)

            # Persist telemetry record in session state for latency diagnostic & summary reports
            if hasattr(tool_context, "state") and tool_context.state is not None:
                try:
                    if hasattr(tool_context.state, "get"):
                        telemetry_history = tool_context.state.get("temp:_sub_agent_telemetry") or []
                    else:
                        telemetry_history = []
                    
                    telemetry_history.append({
                        "sub_agent": self.name,
                        "duration_ms": round(elapsed_ms, 2),
                        "duration_sec": round(elapsed_sec, 3),
                        "timestamp": start_time,
                        "status": "SUCCESS",
                    })
                    tool_context.state["temp:_sub_agent_telemetry"] = telemetry_history
                except Exception as telemetry_err:
                    logger.warning(f"Could not record sub-agent telemetry in state: {telemetry_err}")

            return result
        except Exception as err:
            elapsed_sec = time.perf_counter() - start_counter
            elapsed_ms = elapsed_sec * 1000.0

            log_msg = (
                f"[SUB_AGENT_DISPATCH_END] sub_agent={self.name} "
                f"duration_ms={elapsed_ms:.2f}ms status=ERROR error={err}"
            )
            logger.error(log_msg)
            call_transcript_logger.error(log_msg)
            raise


def get_sub_agent_telemetry_summary(state_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Retrieves recorded sub-agent latency telemetry records from session state."""
    if not state_dict:
        return []
    return state_dict.get("temp:_sub_agent_telemetry", [])
