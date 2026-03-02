import os
import time
import random

# "REALISTIC" = full realistic delays (e.g. 5-30s for Employment)
# "DEMO" = fast but noticeable delays (e.g. 1-2s)
# "TESTING" = 0s delay - DEFAULT
LATENCY_MODE = os.getenv("LATENCY_MODE", "TESTING")

import asyncio

import json

FAILURE_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "failure_configs.json")

def set_service_failure(service_name: str, is_down: bool):
    """Sets the failure state for a specific service."""
    configs = {}
    if os.path.exists(FAILURE_CONFIG_FILE):
        try:
            with open(FAILURE_CONFIG_FILE, "r") as f:
                configs = json.load(f)
        except: pass
    
    configs[service_name] = is_down
    with open(FAILURE_CONFIG_FILE, "w") as f:
        json.dump(configs, f)

def is_service_down(service_name: str) -> bool:
    """Checks if a service is currently marked as down."""
    if not os.path.exists(FAILURE_CONFIG_FILE):
        return False
    try:
        with open(FAILURE_CONFIG_FILE, "r") as f:
            configs = json.load(f)
            return configs.get(service_name, False)
    except:
        return False

def get_latency(seconds: float):
    if LATENCY_MODE == "TESTING":
        return 0
    elif LATENCY_MODE == "DEMO":
        return min(seconds, 1.5)
    return seconds

def simulate_delay(seconds: float):
    """Sleeps for 'seconds' (blocking)."""
    delay = get_latency(seconds)
    if delay > 0:
        time.sleep(delay)

async def simulate_delay_async(seconds: float):
    """Sleeps for 'seconds' (non-blocking)."""
    delay = get_latency(seconds)
    if delay > 0:
        await asyncio.sleep(delay)
