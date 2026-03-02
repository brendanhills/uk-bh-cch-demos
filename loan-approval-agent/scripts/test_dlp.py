import os
from loan_agent.utils.dlp_guardian import inspect_and_mask

def test_dlp_integration():
    """Manual script to verify DLP integration."""
    print("\n--- DLP Integration Test ---")
    
    test_cases = [
        "My Social Security Number is 411-55-6789.",
        "Contact me at sarah.speed@example.com or call 555-0199.",
        "The applicant's name is Sarah Speed.",
        "Safe text with no PII."
    ]
    
    for text in test_cases:
        masked = inspect_and_mask(text)
        print(f"Original: {text}")
        print(f"Masked:   {masked}")
        print("-" * 30)

if __name__ == "__main__":
    test_dlp_integration()
