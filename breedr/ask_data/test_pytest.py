from typing import Any, Literal
import logging
from vertexai.generative_models import GenerativeModel, SafetySetting
from unittest.mock import MagicMock
import pytest

from ask_data import inc_dec
from ask_data.ask_data_core import AskData

format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger()
fhandler = logging.FileHandler(filename='mylog.log', mode='a')
formatter = logging.Formatter(format_string)
fhandler.setFormatter(formatter)
#logger.addHandler(fhandler)
logging.basicConfig(format=format_string,
                     level=logging.INFO, stream=sys.stdout)
logger.setLevel(logging.INFO)

   # The code to test

def test_increment():
    assert inc_dec.increment(3) == 4

# This test is designed to fail for demonstration purposes.
def test_decrement():
    assert inc_dec.decrement(3) == 2


DEFAULT_MODEL_NAME = "gemini-1.5-flash-001"
DEFAULT_SAFETY_SETTING = SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
PROJECT_ID = "uk-bh-experiments-argolis"
REGION = "us-central1"


def test_ask_data_initialization():
    project_id = PROJECT_ID
    region = REGION

    ask_data = AskData(project_id, region)

    assert ask_data.project_id == project_id
    assert ask_data.region == region
    assert ask_data.model_name == DEFAULT_MODEL_NAME
    assert ask_data.safety_setting == DEFAULT_SAFETY_SETTING
    assert isinstance(ask_data.model, GenerativeModel)

def test_convert_instructions_to_yaml():
    text = """
        dob: Is a field of date of birth in YYYY-MM-DD (ISO 8601) format in the attached animals table
        date_moved_to_farm: Is a field of date that the animal was moved to the farm in YYYY-MM-DD (ISO 8601) format in the attached animals table    
        """
    expected_yaml = """
        fields:
        dob:
            description: "Date of birth in YYYY-MM-DD (ISO 8601) format"
            table: animals
            type: date

        date_moved_to_farm:
            description: "Date the animal was moved to the farm in YYYY-MM-DD (ISO 8601) format"
            table: animals
            type: date
    """
    ask_data = AskData(PROJECT_ID, REGION)
    yaml = ask_data.convert_instructions_to_yaml(text)
    logger.debug(yaml)
    assert "yaml" in yaml
    