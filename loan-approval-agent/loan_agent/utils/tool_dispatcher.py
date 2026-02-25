from typing import Dict, Any, Callable
import importlib 

# Registry of available tools (MCP-Lite)
# Maps "tool_name" -> (module_path, function_name)
TOOL_REGISTRY = {
    "get_credit_report": ("external_services.credit_bureau", "get_credit_report"),
    "verify_employment": ("external_services.employment_registry", "verify_employment"),
    "check_fraud_risk": ("external_services.fraud_service", "check_fraud_risk"),
    # Add new tools here
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
