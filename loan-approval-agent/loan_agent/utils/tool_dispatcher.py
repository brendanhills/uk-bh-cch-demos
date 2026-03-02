from typing import Dict, Any, Callable
import importlib 

# --- TOOL REGISTRY (MCP-Lite) ---
# This mimics the Model Context Protocol (MCP) server pattern.
# It decouples the Agent from the underlying implementation, allowing us to
# swap "Mock Services" for "Real Bank APIs" by simply updating this mapping.
TOOL_REGISTRY = {
    "get_credit_report": ("external_services.credit_bureau", "get_credit_report"),
    "verify_employment": ("external_services.employment_registry", "verify_employment"),
    "check_fraud_risk": ("external_services.fraud_service", "check_fraud_risk"),
    "get_ml_risk_score": ("external_services.risk_scoring", "get_ml_risk_score"),
    "lookup_historical_decisions": ("external_services.historical_decisions", "lookup_historical_decisions"),
}

import inspect

async def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches a tool call to the local implementation.
    Mimics an MCP server's "CallTool" request.
    
    Args:
        tool_name: The name of the tool (e.g. "get_credit_report").
        arguments: Dictionary of arguments for the function.
        
    Returns:
        Dict: The result of the tool execution.
    """
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Tool '{tool_name}' not found in registry."}
    
    module_path, func_name = TOOL_REGISTRY[tool_name]
    
    try:
        # Dynamic Import (Lazy Loading)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        
        # Call the function
        print(f"[ToolDispatcher] Calling {tool_name} with {arguments.keys()}")
        
        if inspect.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)
            
        return result
        
    except ImportError as e:
        return {"error": f"Configuration Error: Could not import {module_path}: {e}"}
    except Exception as e:
        return {"error": f"Tool Execution Error ({tool_name}): {str(e)}"}

def list_tools() -> Dict[str, Any]:
    """Returns the list of registered tools."""
    return TOOL_REGISTRY
