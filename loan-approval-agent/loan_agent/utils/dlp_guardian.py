import os
import google.auth
from typing import Optional
from google.cloud import dlp_v2

# --- GLOBAL CONFIG ---
_DLP_CLIENT: Optional[dlp_v2.DlpServiceClient] = None
_DLP_PARENT: Optional[str] = None

def _get_client():
    """Lazy initializer for the DLP client."""
    global _DLP_CLIENT, _DLP_PARENT
    if _DLP_CLIENT:
        return _DLP_CLIENT, _DLP_PARENT

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
    if not project_id:
        try:
            _, project_id = google.auth.default()
        except Exception as e:
            raise RuntimeError(f"Failed to resolve Project ID for DLP: {e}")

    _DLP_CLIENT = dlp_v2.DlpServiceClient()
    _DLP_PARENT = f"projects/{project_id}/locations/global"
    print(f"[DLP] Initialized Cloud DLP for project: {project_id}")
    return _DLP_CLIENT, _DLP_PARENT

def inspect_and_mask(text: str) -> str:
    """
    Scans text for PII using Cloud DLP and replaces it with [INFO_TYPE].
    """
    if not text:
        return ""

    try:
        client, parent = _get_client()
        
        # Configure inspection & de-identification
        request = {
            "parent": parent,
            "inspect_config": {
                "info_types": [
                    {"name": "US_SOCIAL_SECURITY_NUMBER"},
                    {"name": "EMAIL_ADDRESS"},
                    {"name": "PHONE_NUMBER"},
                    {"name": "CREDIT_CARD_NUMBER"},
                    {"name": "PERSON_NAME"}
                ],
                "min_likelihood": dlp_v2.Likelihood.LIKELIHOOD_UNSPECIFIED,
            },
            "deidentify_config": {
                "info_type_transformations": {
                    "transformations": [
                        {
                            "primitive_transformation": {
                                "replace_with_info_type_config": {}
                            }
                        }
                    ]
                }
            },
            "item": {"value": text},
        }
        
        response = client.deidentify_content(request=request)
        return response.item.value

    except Exception as e:
        print(f"[DLP] Cloud DLP call failed: {e}")
        return f"[DLP_ERROR: {str(e)[:50]}...]"

def reset_dlp():
    """Helper for testing to force re-initialization."""
    global _DLP_CLIENT, _DLP_PARENT
    _DLP_CLIENT = None
    _DLP_PARENT = None
