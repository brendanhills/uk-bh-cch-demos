from typing import Optional

# Mock Token Vault (Simulating Google Cloud DLP / Sensitive Data Protection)
# In production, this would be a secure, encrypted database or DLP Service.

_TOKEN_MAP = {
    "900-00-1234": "user_01",   # Sarah Speed
    "900-00-5678": "user_02",  # David Leverage (Jumbo Loan)
    "900-00-9012": "user_03",  # Maria Agility (Gift)
    "900-00-3456": "user_04",  # Gary Escalate (Risk)
    "900-00-9999": "user_05",  # Jane Fraud (Fraud?)
    "000-00-0000": "user_99",  # Alex Random (Unknown)
}

_REVERSE_MAP = {v: k for k, v in _TOKEN_MAP.items()}

def tokenize(gov_id: str) -> str:
    """
    Exchanges a PII (Gov ID) for an Opaque Token.
    Simulates: client.projects.locations.content.deidentify(...)
    """
    if gov_id in _TOKEN_MAP:
        return _TOKEN_MAP[gov_id]
        
    # Dynamic Tokenization for new users in demo
    token = f"user_{abs(hash(gov_id)) % 1000:03d}"
    _TOKEN_MAP[gov_id] = token
    _REVERSE_MAP[token] = gov_id
    return token

def detokenize(token: str) -> Optional[str]:
    """
    Exchanges an Opaque Token back to PII (Gov ID) within the Secure Boundary.
    """
    return _REVERSE_MAP.get(token)
