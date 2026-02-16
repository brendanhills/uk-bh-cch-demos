import pytest
import os
import shutil
from loan_approval_agent.audit_logger import AuditLogger

@pytest.fixture
def clean_audit_dir():
    """Fixture to clean up audit logs before/after tests."""
    log_dir = "loan_approval_agent/data/audit_logs"
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    yield
    # Cleanup after test
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

def test_audit_logger_sanitization(clean_audit_dir):
    """Test that AuditLogger sanitizes unsafe applicant IDs."""
    
    # Test case 1: ID with forward slash
    logger1 = AuditLogger("user/123")
    assert "user_123" in logger1.log_file or "user123" in logger1.log_file
    assert "/" not in os.path.basename(logger1.log_file)
    
    # Test case 2: ID with backward slash (less likely on linux but good to test)
    logger2 = AuditLogger(r"user\456")
    assert "\\" not in os.path.basename(logger2.log_file)
    
    # Test case 3: "N/A" (The specific failure case)
    logger3 = AuditLogger("N/A")
    assert "audit_NA.json" in logger3.log_file or "audit_N_A.json" in logger3.log_file
    
    # Ensure files can be created
    logger1.log_event("test_agent", "test_action", {})
    assert os.path.exists(logger1.log_file)
    
    logger3.log_event("test_agent", "test_action", {})
    assert os.path.exists(logger3.log_file)
