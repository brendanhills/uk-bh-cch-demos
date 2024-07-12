import vertexai

from vertexai.generative_models import GenerationConfig, GenerativeModel

# TODO(developer): Update and un-comment below line
project_id = "uk-bh-experiments-agolis"
vertexai.init(project=project_id, location="us-central1")

response_schema = {
    "type": "OBJECT",
    "properties": {
        "forecast": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "Day": {"type": "STRING"},
                    "Forecast": {"type": "STRING"},
                    "Humidity": {"type": "STRING"},
                    "Temperature": {"type": "INTEGER"},
                    "Wind Speed": {"type": "INTEGER"},
                },
                "required": ["Day", "Temperature", "Forecast"],
            },
        }
    },
}

prompt = """
    The week ahead brings a mix of weather conditions.
    Sunday is expected to be sunny with a temperature of 77°F and a humidity level of 50%. Winds will be light at around 10 km/h.
    Monday will see partly cloudy skies with a slightly cooler temperature of 72°F and humidity increasing to 55%. Winds will pick up slightly to around 15 km/h.
    Tuesday brings rain showers, with temperatures dropping to 64°F and humidity rising to 70%. Expect stronger winds at 20 km/h.
    Wednesday may see thunderstorms, with a temperature of 68°F and high humidity of 75%. Winds will be gusty at 25 km/h.
    Thursday will be cloudy with a temperature of 66°F and moderate humidity at 60%. Winds will ease slightly to 18 km/h.
    Friday returns to partly cloudy conditions, with a temperature of 73°F and lower humidity at 45%. Winds will be light at 12 km/h.
    Finally, Saturday rounds off the week with sunny skies, a temperature of 80°F, and a humidity level of 40%. Winds will be gentle at 8 km/h.
"""

model = GenerativeModel("gemini-1.5-pro-001")

response = model.generate_content(
    prompt,
    generation_config=GenerationConfig(
        response_mime_type="application/json", response_schema=response_schema
    ),
)

print(response.text)