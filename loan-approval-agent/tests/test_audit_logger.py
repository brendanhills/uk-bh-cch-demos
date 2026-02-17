import pytest
import os
import shutil
import json
from loan_approval_agent.tools.audit_logger import log_event, LOG_FILE, LOG_DIR

@pytest.fixture
def clean_audit_dir():
    """Fixture to clean up audit logs before/after tests."""
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)
    yield
    # Cleanup after test
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)

def test_audit_logger_creates_file(clean_audit_dir):
    """Test that log_event creates the log file and writes to it."""
    log_event("user123", "TEST_EVENT", {"foo": "bar"})
    
    assert os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["applicant_id"] == "user123"
        assert entry["event_type"] == "TEST_EVENT"
        assert entry["details"]["foo"] == "bar"

def test_audit_logger_masks_pii(clean_audit_dir):
    """Test that PII is masked in the logs."""
    sensitive_data = {
        "ssn": "123-45-6789",
        "nested": {
            "account_number": "123456789",
            "safe": "value"
        },
        "description": "User has SSN 123-45-6789 in text."
    }
    
    log_event("user456", "SENSITIVE_EVENT", sensitive_data)
    
    with open(LOG_FILE, "r") as f:
        line = f.readlines()[0]
        entry = json.loads(line)
        details = entry["details"]
        
        # Check direct key masking
        assert details["ssn"] == "***-**-****"
        
        # Check nested key masking
        assert details["nested"]["account_number"] == "*****"
        assert details["nested"]["safe"] == "value"
        
        # Check regex masking in string (if implemented)
        # The current implementation checks for SSN regex in strings
        assert "***-**-****" in details["description"]
        assert "123-45-6789" not in details["description"]
