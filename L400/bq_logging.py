import json
import vertexai
from google import genai
from google.cloud import bigquery
from typing import Any, List, Dict, Type
from vertexai.preview.generative_models import GenerativeModel

MODEL="gemini-3-flash-preview"  # Change as needed.
PROJECT="uk-bh-experiments-argolis"
LOCATION="global"  # Change as needed.
BQ_URI="bq://uk-bh-experiments-argolis.gemini_logging.l400"  # Existing BigQuery dataset in the same project with model endpoint. Data will be written to this table name.
OUTPUT_FILE="./gemini_task_analysis_data.jsonl"

# Enable inference logging according to https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/request-response-logging#python-sdk
vertexai.init(project=PROJECT, location=LOCATION)
model = GenerativeModel(MODEL)
# This adds logging to the model, as identified by the name of the model endpoint (e.g., "gemini-3-flash-preview"). Until disabled, all requests from this project to this model will be logged.
model.set_request_response_logging_config(enabled=True, sampling_rate=1.0, bigquery_destination=BQ_URI, enable_otel_logging=True)
print(f"Enabled logging for {MODEL} in {PROJECT} ({LOCATION}). Remember to turn it off!")

# Do all your Gemini inference. Unknown if you have to initialize the client after set_request_response_logging or if logging works if you've already initialized the client.

# Disable BigQuery logging
model.set_request_response_logging_config(enabled=False, sampling_rate=1.0, bigquery_destination=BQ_URI)
print(f"Disabled logging for {MODEL} in {PROJECT} ({LOCATION}).")


# Turn the BigQuery logs into jsonl compatible with Gemini Task Analysis.
# Note you can run this code below in any environment that has read access to the BQ logs data you created with the code above.

bqclient = bigquery.Client(project=PROJECT)

clean_uri = BQ_URI.replace("bq://", "")
sql_query = f"SELECT * FROM `{clean_uri}`"
request_df = bqclient.query(sql_query).to_dataframe()

# View the first few rows
print(request_df.head())

def write_jsonl_external(
   data: List[Dict[str, Any]],
   path: str,
   json_encoder_cls: Type[json.JSONEncoder] = None,
):
 """Writes a list of dicts to a jsonl file.

 This version is suitable for running outside of Google's
 internal environment.

 Args:
   data: A list of dicts.
   path: The path to the output jsonl file.
   json_encoder_cls: A custom JSONEncoder class to handle
     serialization of complex types.
 """
 try:
   with open(path, 'w', encoding='utf-8') as f:
     for item in data:
       f.write(json.dumps(item, cls=json_encoder_cls) + '\n')
 except (IOError, TypeError, json.JSONDecodeError) as e:
   print(f"Error writing to {path}: {e}")

request_dicts = [json.loads(x) for x in request_df.full_request]
write_jsonl_external(request_dicts, OUTPUT_FILE)


