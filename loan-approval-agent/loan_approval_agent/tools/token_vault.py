
from typing import Optional

# Mock Token Vault (Simulating Google Cloud DLP / Sensitive Data Protection)
# In production, this would be a secure, encrypted database or DLP Service.

_TOKEN_MAP = {
    "900-00-1234": "user_01",   # Sarah Jenkins
    "900-00-5678": "user_02",  # David (Jumbo Loan)
    "900-00-9012": "user_03",  # Maria (Gift)
    "900-00-3456": "user_04",  # Gary (Risk)
    "900-00-9999": "user_05",  # Jane (Fraud?)
    "000-00-0000": "user_99",  # Ghost (Unknown)
}

_REVERSE_MAP = {v: k for k, v in _TOKEN_MAP.items()}

def tokenize(gov_id: str) -> str:
    """
    Exchanges a PII (Gov ID) for an Opaque Token.
    Simulates: client.projects.locations.content.deidentify(...)
    """
    # OPTIONAL: Real DLP Implementation
    # if REAL_DLP_ENABLED:
    #     parent = f"projects/{PROJECT_ID}/locations/global"
    #     item = {"value": gov_id}
    #     response = dlp.deidentify_content(request={"parent": parent, "item": item, "deidentify_config": ...})
    #     return response.item.value
    
    return _TOKEN_MAP.get(gov_id, f"user_{hash(gov_id) % 1000}")

def detokenize(token: str) -> Optional[str]:
    """
    Exchanges an Opaque Token back to PII (Gov ID) within the Secure Boundary.
    """
    return _REVERSE_MAP.get(token)
