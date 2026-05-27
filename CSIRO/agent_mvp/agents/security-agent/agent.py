import os
from typing import List
from google.adk import Agent
from google.adk.tools import FunctionTool

# --- Mock Security Policy ---
SECURITY_POLICY = """
CSIRO SECURITY POLICY:
1. No hardcoded credentials (API keys, passwords).
2. No inclusion of personal identifying information (PII).
3. No use of deprecated cryptographic libraries (e.g., md5).
4. All database queries must use parameterized statements to prevent SQL injection.
5. Internal IP addresses or server names must not be exposed in public-facing code.
"""

# --- Mock GitHub Tool ---
def fetch_github_diff(repo: str, commit_id: str) -> str:
    """Fetches a mock diff for a given repo and commit."""
    # Mocking a problematic commit
    if commit_id == "commit-123":
        return """
diff --git a/src/config.py b/src/config.py
index e69de29..4b58e33 100644
--- a/src/config.py
+++ b/src/config.py
@@ -1,3 +1,4 @@
-API_URL = "https://api.example.com"
+API_URL = "https://api.internal.csiro.au"
+DB_PASSWORD = "super-secret-password-123"
+SECRET_KEY = "md5:123456"
"""
    return """
diff --git a/README.md b/README.md
index e69de29..4b58e33 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,2 @@
 # Project
+This is a safe project.
"""

fetch_github_diff_tool = FunctionTool(func=fetch_github_diff)

# --- Security Agent ---
security_agent = Agent(
    name="security_analyst",
    model="gemini-2.0-flash-001",
    instruction=f"""You are a CSIRO Security Analyst Agent. 
    Your task is to analyze GitHub diffs and identify violations of the CSIRO Security Policy.
    
    POLICY:
    {SECURITY_POLICY}
    
    When a user provides a repo and commit ID, fetch the diff and provide a detailed report of any violations.
    If no violations are found, state that the changes are compliant.""",
    tools=[fetch_github_diff_tool]
)
