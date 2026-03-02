import pytest
import os
from loan_agent import config

@pytest.fixture(autouse=True, scope="session")
def setup_test_env():
    """Ensure tests always run in TESTING mode and fail fast."""
    os.environ["LATENCY_MODE"] = "TESTING"
    config.LATENCY_MODE = "TESTING"
    
    # Optional: ensure project/location are set or None as required by the environment
    # os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
    # os.environ.pop("GOOGLE_CLOUD_LOCATION", None)
