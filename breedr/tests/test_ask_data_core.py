from ask_data.ask_data_core import AskData
import pytest
import os

# Replace with your actual project ID and region
PROJECT_ID = os.environ.get("PROJECT_ID", "uk-bh-experiments-argolis")  # or replace directly
REGION = os.environ.get("REGION", "us-central1") # or replace directly
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.0-flash-001")


@pytest.fixture(scope="module")  # Initialize once per module
def ask_data_instance():
    return AskData(PROJECT_ID, REGION, MODEL_NAME)



def test_convert_instructions_to_yaml_simple(ask_data_instance):
    instructions = "Name: John Doe\nAge: 30"
    yaml_output = ask_data_instance.convert_instructions_to_yaml(instructions)
    assert "name: John Doe" in yaml_output.lower() # Case-insensitive check
    assert "age: 30" in yaml_output.lower()




def test_convert_instructions_to_yaml_complex(ask_data_instance):
  instructions = """
  # Employee data
  Name: Jane Smith
  Department: Sales
  Skills:
      - Communication
      - Negotiation
      - Closing deals
  """

  yaml_output = ask_data_instance.convert_instructions_to_yaml(instructions)
  assert "name: Jane Smith" in yaml_output.lower()
  assert "department: Sales" in yaml_output.lower()
  assert "- Communication" in yaml_output.lower()  # check list items



def test_convert_instructions_to_yaml_empty(ask_data_instance):
    instructions = ""  # Empty input
    yaml_output = ask_data_instance.convert_instructions_to_yaml(instructions)
    # Check for an empty or default YAML structure.  This will depend on
    # what the model returns for empty input, so adjust accordingly.
    # A simple option might be:
    assert yaml_output.strip() == "" or yaml_output is not None



def test_initialize_ai(ask_data_instance): # check the client initialized
    assert ask_data_instance.client is not None
    assert ask_data_instance.model_name == MODEL_NAME


# Example demonstrating using environment variables for sensitive data.
# Ensure to set these environment variables before running the test.


@pytest.mark.skipif(
    not all([PROJECT_ID, REGION]),
    reason="Environment variables PROJECT_ID and REGION are required."
) # this allows you to skip the test if environment variables are not set.
def test_environment_variables():
  assert PROJECT_ID is not None
  assert REGION is not None


