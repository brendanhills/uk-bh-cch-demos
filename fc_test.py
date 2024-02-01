import requests
from vertexai.preview import generative_models
from vertexai.preview.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool
)
model = GenerativeModel("gemini-pro")

get_current_weather_func = generative_models.FunctionDeclaration(
  name="get_current_weather",
  description="Get the current weather in a given location",
  parameters={
      "type": "object",
      "properties": {
          "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
              "type": "string",
              "enum": [
                  "celsius",
                  "fahrenheit",
              ]
          }
      },
      "required": [
          "location"
      ]
  },
)

weather_tool = generative_models.Tool(
  function_declarations=[get_current_weather_func]
)

model_response = model.generate_content(
    "What is the weather like in London, UK?",
    generation_config={"temperature": 0},
    tools=[weather_tool],
)

print("model_response\n", model_response)

get_location = FunctionDeclaration(
    name="get_location",
    description="Get latitude and longitude for a given location",
    parameters={
        "type": "object",
        "properties": {
            "poi": {"type": "string", "description": "Point of interest"},
            "street": {"type": "string", "description": "Street name"},
            "city": {"type": "string", "description": "City name"},
            "county": {"type": "string", "description": "County name"},
            "state": {"type": "string", "description": "State name"},
            "country": {"type": "string", "description": "Country name"},
            "postal_code": {"type": "string", "description": "Postal code"},
        },
    },
)

location_tool = Tool(
    function_declarations=[get_location],
)


prompt = """
I want to get the lat/lon coordinates for the following address:
1600 Amphitheatre Pkwy, Mountain View, CA 94043, US
"""

response = model.generate_content(
    prompt,
    generation_config={"temperature": 0},
    tools=[location_tool],
)
response.candidates[0].content.parts[0]


x = response.candidates[0].content.parts[0].function_call.args

url = "https://nominatim.openstreetmap.org/search?"
for i in x:
  print(f'{i} = {x[i]}')
  url += '{}="{}"&'.format(i, x[i])
url += "format=json"

print(f'{url}')
x = requests.get(url)
content = x.json()
print(f'{content}')