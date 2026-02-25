from loan_agent import config # Loads .env
from loan_agent.utils.dlp_guardian import guardian
import os

def test_dlp():
    print("=== Testing DLP Guardian ===")
    print(f"DEBUG: GOOGLE_CLOUD_PROJECT = {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    # Force init to check client
    is_cloud = guardian.client is not None
    print(f"Mode: {'Cloud DLP' if is_cloud else 'Regex Fallback'}")
    
    sample_text = "My SSN is 900-00-1234 and my email is sarah.speed@example.com."
    print(f"\nOriginal: {sample_text}")
    
    masked = guardian.inspect_and_mask(sample_text)
    print(f"Masked:   {masked}")
    
    if "[REDACTED" in masked:
        print("\n✅ Redaction successful.")
    else:
        print("\n❌ Redaction failed.")

if __name__ == "__main__":
    test_dlp()
