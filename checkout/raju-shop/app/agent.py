# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
import os
import google.auth
import json


def load_inventory() -> dict:
    """Loads inventory from a JSON file."""
    with open(os.path.join(os.path.dirname(__file__), "inventory.json"), "r") as f:
        return json.load(f)

INVENTORY = load_inventory()

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def check_inventory(item_name: str) -> str:
    """Checks the inventory for a given item, including price, stock, and cost.

    Args:
        item_name: The name of the item to check.

    Returns:
        A string with the price, stock, and cost information, or a message if the item is not found.

    """
    
    item = INVENTORY.get(item_name)
    if item:
        return (
            f"'{item_name}' details: Price: {item['price']} coins, Stock: {item['stock']}, Cost: {item['cost']} coins."
        )
    return f"Sorry, I don't have '{item_name}' in my inventory."


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=f"""You are Raju, a bargaining shopkeeper in a digital bazaar. Your goal is to sell high and be funny. Speak with an Indian-English flair.

Your inventory is: {', '.join(INVENTORY.keys())}.

When a customer asks about an item, figure out which item from your inventory they mean, even if they misspell it. Then, use the check_inventory tool with the correct item name.

The 'cost' from the tool is your secret cost price. You must not sell for less than the cost, and you must NEVER reveal the cost to the customer!""",
    tools=[check_inventory],
)

app = App(
    root_agent=root_agent,
    name="app",
)
