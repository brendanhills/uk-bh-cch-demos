import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

DEFAULT_MODEL_NAME = "gemini-1.5-flash-001"
DEFAULT_SAFETY_SETTING = SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH

import logging
logger = logging.getLogger()


class AskData:

  def __init__(self, project_id, region, model_name=DEFAULT_MODEL_NAME, safety_setting=DEFAULT_SAFETY_SETTING):
    self.model_name = model_name
    self.safety_setting = safety_setting
    self.project_id = project_id
    self.region = region
    self.initialize_ai(self.project_id, self.region, self.model_name, self.safety_setting)


  def convert_instructions_to_yaml(self,text: str) -> str:

    generation_config = {
      "max_output_tokens": 8192,
      "temperature": 1,
      "top_p": 0.95,
    }

    insructions_part = Part.from_text(text)
    prompt = """convert this text to structured YAML"""
    response = self.model.generate_content(
      [insructions_part, prompt],
      generation_config=generation_config,
      safety_settings=self.safety_settings,
      stream=False,
    )

    logger.debug(response.text)

    return response.text


  def initialize_ai(self,project_id, region, model_name=DEFAULT_MODEL_NAME, safety_setting=DEFAULT_SAFETY_SETTING) -> None:

    self.model_name = model_name
    self.safety_settings = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=safety_setting
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=safety_setting
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=safety_setting
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=safety_setting
        ),
    ]

    vertexai.init(project=project_id, location=region)
    self.model = GenerativeModel(self.model_name)
