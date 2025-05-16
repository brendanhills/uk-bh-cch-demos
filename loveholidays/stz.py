from google.cloud import aiplatform as aip


# Cloud project id.
PROJECT_ID = "uk-bh-experiments-argolis"  # @param {type:"string"}

# The region you want to launch jobs in.
REGION = "us-central1"  # @param {type:"string"}

# The Cloud Storage bucket for storing experiments output.
BUCKET_URI = "gs://uk-bh-experiments-argolis-us"  # @param {type:"string"}

# The service account looks like:
# '@.iam.gserviceaccount.com'
# Please go to https://cloud.google.com/iam/docs/service-accounts-create#iam-service-accounts-create-console
# and create service account with `Vertex AI User` and `Storage Object Admin` roles.
# The service account for deploying fine tuned model.
SERVICE_ACCOUNT = "vertex-deployment-tuning@uk-bh-experiments-argolis.iam.gserviceaccount.com"  # @param {type:"string"}
SERVE_DOCKER_URI = "us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-open-clip-serve"

# The serving port.
SERVE_PORT = 7080

from datetime import datetime
from typing import Tuple


def get_job_name_with_datetime(prefix: str) -> str:
  """Gets the job name with date time when triggering training or deployment

  jobs in Vertex AI.
  """
  return prefix + datetime.now().strftime("_%Y%m%d_%H%M%S")


def download_image(url: str) -> str:
    """Downloads an image from the given URL.

    Args:
        url: The URL of the image to download.

    Returns:
        base64 encoded image.
    """
    import os

    os.system('wget -O image.jpg $url')
    os.system('base64 image.jpg > image.txt')
    return open("image.txt").read()


def deploy_model(
    model_name: str,
    model_id: str,
    service_account: str,
    task: str,
    precision: str,
    machine_type="n1-standard-8",
    accelerator_type="NVIDIA_TESLA_V100",
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    intial_replica_count=1,
) -> Tuple[aip.Model, aip.Endpoint]:
  """Deploys trained models into Vertex AI."""
  endpoint = aip.Endpoint.create(display_name=f"{model_name}-endpoint")
  serving_env = {
      "MODEL": model_id,
      "TASK": task,
      "PRECISION": precision,
      "DEPLOY_SOURCE": "notebook",
  }
  # If the model_id is a GCS path, use artifact_uri to pass it to serving docker.
  artifact_uri = model_id if model_id.startswith("gs://") else None
  model = aip.Model.upload(
      display_name=model_name,
      serving_container_image_uri=SERVE_DOCKER_URI,
      serving_container_ports=[SERVE_PORT],
      serving_container_predict_route="/predictions/transformers_serving",
      serving_container_health_route="/ping",
      serving_container_environment_variables=serving_env,
      artifact_uri=artifact_uri,
  )
  model.deploy(
    endpoint=endpoint,
    machine_type=machine_type,
    accelerator_type=accelerator_type,
    accelerator_count=accelerator_count,
    deploy_request_timeout=1800,
    service_account=service_account,
    min_replica_count=min_replica_count,
    max_replica_count=max_replica_count,
    #initial_replica_count=intial_replica_count,
  )
  return model, endpoint

def try_model(endpoint):
   import numpy as np

   # # Loads an existing endpoint as below.
   # endpoint_name = endpoint.name
   # aip_endpoint_name = (
   #     f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{endpoint_name}"
   # )
   # endpoint = aiplatform.Endpoint(aip_endpoint_name)

   instances = [
   {
       "text": "This is a photo of adenocarcinoma histopathology",
       "image": download_image(
           "https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224/resolve/main/example_data/biomed_image_classification_example_data/bone_X-ray.jpg"
       ),
   },
   {"text": "This is a photo of brain MRI"},
   {"text": "This is a photo of covid line chart"},
   {"text": "This is a photo of squamous cell carcinoma histopathology"},
   {"text": "This is a photo of immunohistochemistry histopathology"},
   {"text": "This is a photo of bone X-ray"},
   {"text": "This is a photo of chest X-ray"},
   {"text": "This is a photo of hematoxylin and eosin histopathology"},
   {"text": "This is a photo of pie chart"},
   ]
   response = endpoint.predict(instances=instances)

   print(response.predictions)

   selected_idx = np.argmax(response.predictions[0])
   print(f"Selected class: {instances[selected_idx]['text']}")


def main():

    aip.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)

    model_id = "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224"
    model_name = "clip"

    model1, endpoint1 = deploy_model(
        model_name=get_job_name_with_datetime(prefix="biomedclip-serve"),
        model_id=model_id,
        service_account=SERVICE_ACCOUNT,
        task="zero-shot-image-classification",
        precision="amp",
        max_replica_count=3,
        min_replica_count=1,
        intial_replica_count=1
    )

    print("endpoint_name:", endpoint1.name)
    print("model_name:", model1.name)
    print("model_display_name:", model1.display_name)
    try_model(endpoint1)



    model0, endpoint0 = deploy_model(
        model_name=get_job_name_with_datetime(prefix="biomedclip-serve"),
        model_id=model_id,
        service_account=SERVICE_ACCOUNT,
        task="zero-shot-image-classification",
        precision="amp",
        max_replica_count=3,
        min_replica_count=0,
        intial_replica_count=1
    )

    print("endpoint_name:", endpoint0.name)
    print("model_name:", model0.name)
    print("model_display_name:", model0.display_name)
    
    try_model(endpoint0)


if __name__ == "__main__":
    main()


