from google import genai
from google.genai import types
from google.genai.types import Part, SafetySetting

DEFAULT_MODEL_NAME = "gemini-2.0-flash-001"

import logging
logger = logging.getLogger()


class AskData:

  client = None

  def __init__(self, project_id, region, model_name=DEFAULT_MODEL_NAME):
    self.model_name = model_name
    self.project_id = project_id
    self.region = region
    self.initialize_ai(self.project_id, self.region, self.model_name)


  def convert_instructions_to_yaml(self,text: str) -> str:

    generation_config = types.GenerateContentConfig(
      temperature=1,
      top_k=40,
      top_p=0.95,
      max_output_tokens=8192,
      response_modalities = ["TEXT"],
      safety_settings=self.safety_settings
    )

    instructions_part = Part.from_text(text=text)
    prompt_part = Part.from_text(text=f"""convert this text to structured YAML""")

    contents = [
      types.Content(
        role="user",
        parts=[instructions_part, prompt_part]
      )
    ]
    response = self.client.models.generate_content(
      model=self.model_name,
      contents = contents,
      config=generation_config
      )

    logger.debug(response.text)

    return response.text



  def initialize_ai(self,project_id, region, model_name=DEFAULT_MODEL_NAME) -> None:

    self.model_name = model_name

    self.safety_settings = [types.SafetySetting(
          category="HARM_CATEGORY_HATE_SPEECH",
          threshold="OFF"
        ),types.SafetySetting(
          category="HARM_CATEGORY_DANGEROUS_CONTENT",
          threshold="OFF"
        ),types.SafetySetting(
          category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
          threshold="OFF"
        ),types.SafetySetting(
          category="HARM_CATEGORY_HARASSMENT",
          threshold="OFF"
        )]
    self.client = genai.Client(
      vertexai=True,
      project=project_id,
      location=region
    )

    


