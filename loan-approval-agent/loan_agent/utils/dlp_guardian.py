import re
import os
from typing import Optional
import warnings

# Pattern for Social Security Numbers (Simple Regex Fallback)
SSN_PATTERN = r"\d{3}-\d{2}-\d{4}"
# Pattern for Email (Fallback)
EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

class DLPGuardian:
    """
    Guards sensitive data (PII) from entering logs or non-secure contexts.
    
    In Production: Wraps `google.cloud.dlp_v2`.
    In Demo: Uses robust Regex for speed and offline capability, unless configured otherwise.
    """
    def __init__(self):
        self._client = None
        self._parent = None
        self._use_cloud_dlp_checked = False
        self._project_id = None

    @property
    def client(self):
        if not self._use_cloud_dlp_checked:
            self._initialize_client()
        return self._client

    def _initialize_client(self):
        self._project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
        
        # Try to find it via google.auth if env var is missing
        if not self._project_id:
             try:
                 import google.auth
                 _, self._project_id = google.auth.default()
             except Exception:
                 pass

        if self._project_id:
            try:
                from google.cloud import dlp_v2
                self._client = dlp_v2.DlpServiceClient()
                self._parent = f"projects/{self._project_id}/locations/global"
                print(f"[DLP] Initialized Cloud DLP for project: {self._project_id}")
            except ImportError:
                print("[DLP] google-cloud-dlp not installed. Using Regex fallback.")
            except Exception as e:
                print(f"[DLP] Failed to initialize Cloud DLP: {e}. Using Regex fallback.")
        else:
             print("[DLP] No PROJECT_ID found. Using Regex fallback.")
        
        self._use_cloud_dlp_checked = True

    def inspect_and_mask(self, text: str) -> str:
        """
        Scans text for PII and replaces it with [REDACTED_TYPE].
        """
        if not text:
            return ""

        # Trigger lazy init
        if self.client:
            try:
                return self._call_cloud_dlp(text)
            except Exception as e:
                # Fallback on error
                print(f"[DLP] Error checking content: {e}")
                return self._regex_mask(text)
        
        return self._regex_mask(text)

    def _call_cloud_dlp(self, text: str) -> str:
        # Client is already ensured to exist if we are here
        from google.cloud import dlp_v2
        
        # Prepare the item
        item = {"value": text}
        
        # Configure inspection (what to look for)
        inspect_config = {
            "info_types": [
                {"name": "US_SOCIAL_SECURITY_NUMBER"},
                {"name": "EMAIL_ADDRESS"},
                {"name": "PHONE_NUMBER"},
                {"name": "CREDIT_CARD_NUMBER"},
                {"name": "PERSON_NAME"} # Be careful with names, might over-redact
            ],
            "min_likelihood": dlp_v2.Likelihood.LIKELIHOOD_UNSPECIFIED,
        }
        
        # Configure de-identification (how to mask)
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        "primitive_transformation": {
                            "replace_with_info_type_config": {} # Replaces with [INFO_TYPE]
                        }
                    }
                ]
            }
        }
        
        response = self._client.deidentify_content(
            request={
                "parent": self._parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,
            }
        )
        
        return response.item.value

    def _regex_mask(self, text: str) -> str:
        # Redact SSNs
        masked_text = re.sub(SSN_PATTERN, "[REDACTED_SSN]", text)
        # Redact Emails
        masked_text = re.sub(EMAIL_PATTERN, "[REDACTED_EMAIL]", masked_text)
        return masked_text

    def deidentify(self, text: str) -> str:
        return self.inspect_and_mask(text)

    def reset(self):
        """Reset singleton state for testing."""
        self._client = None
        self._parent = None
        self._use_cloud_dlp_checked = False
        self._project_id = None

# Singleton instance
guardian = DLPGuardian()

def sanitize_log_message(message: str) -> str:
    """Helper for audit logger"""
    return guardian.inspect_and_mask(message)
