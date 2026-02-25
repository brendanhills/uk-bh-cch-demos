import os
import time
import random

# "REALISTIC" = full realistic delays (e.g. 5-30s for Employment)
# "DEMO" = fast but noticeable delays (e.g. 1-2s) - DEFAULT
# "TESTING" = 0s delay
LATENCY_MODE = os.getenv("LATENCY_MODE", "DEMO")

import asyncio

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
