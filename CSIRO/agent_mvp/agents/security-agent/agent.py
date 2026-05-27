import os
from google.adk import Agent
from google.adk.tools import FunctionTool

# --- Load Realistic Policy Document ---
POLICY_FILE = os.path.join(os.path.dirname(__file__), "security_policy_ssds.md")
if os.path.exists(POLICY_FILE):
    try:
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            SECURITY_POLICY = f.read()
    except Exception as e:
        SECURITY_POLICY = f"Error reading policy file: {str(e)}"
else:
    # Minimal fallback in case file is deleted
    SECURITY_POLICY = """
    CSIRO SECURITY POLICY (Fallback):
    1. Zero hardcoded secrets in source files.
    2. No deprecated cryptography libraries (e.g., md5, sha1).
    3. Dependencies must be pinned exactly (no wildcards, no 'latest' tags).
    4. Database queries must use parameterized prepared statements.
    5. Strategic/Critical projects (e.g., 'Project Genesis') must not be on public repositories.
    6. Machine learning models must be in non-executable formats (e.g., safetensors).
    """

# --- Expanded Mock GitHub Tool ---
def fetch_github_diff(repo: str, commit_id: str) -> str:
    """Fetches a mock git diff for a given repo and commit ID to analyze."""
    
    # 1. Compliant Commit
    if commit_id == "commit-safe":
        return """
diff --git a/src/processor.py b/src/processor.py
index e69de29..4b58e33 100644
--- a/src/processor.py
+++ b/src/processor.py
@@ -1,6 +1,8 @@
 import os
+import bcrypt
 
-def process_data(data):
-    return data.strip()
+def hash_user_password(raw_password: str) -> bytes:
+    # Compliant password hashing using bcrypt as recommended
+    salt = bcrypt.gensalt()
+    return bcrypt.hashpw(raw_password.encode('utf-8'), salt)
"""

    # 2. Secret & Deprecated Crypto Violations
    elif commit_id == "commit-secrets":
        return """
diff --git a/src/auth.py b/src/auth.py
index a11b223..c44f556 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,5 +1,8 @@
 import hashlib
 
+# VIOLATION: Zero-Credential Policy (3.1) - Hardcoded Client Password and Token
+DB_PASSWORD = "csiro-admin-secret-pwd-2026"
+API_KEY = "xoxb-1234567890-abcdef"
+
 def hash_token(token: str) -> str:
-    return token
+    # VIOLATION: Cryptography Standard (3.4) - Banned insecure hash algorithm (MD5)
+    return hashlib.md5(token.encode()).hexdigest()
"""

    # 3. Supply Chain (Unpinned Dependency) Violation
    elif commit_id == "commit-dependencies":
        return """
diff --git a/pyproject.toml b/pyproject.toml
index b99d332..f44e112 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -7,5 +7,8 @@ dependencies = [
     "fastapi>=0.110.0",
-    "numpy==1.26.4",
+    # VIOLATION: Supply Chain (3.2) - Unpinned dependency wildcard (*)
+    "numpy=*",
+    # VIOLATION: Supply Chain (3.2) - Unpinned 'latest' tag
+    "scipy=latest"
 ]
"""

    # 4. Critical Repo Classification & Executable Model Violations
    elif commit_id == "commit-ai-model":
        return """
diff --git a/scripts/inference.py b/scripts/inference.py
index d22c118..e88d991 100644
--- a/scripts/inference.py
+++ b/scripts/inference.py
@@ -1,4 +1,7 @@
-import safetensors
+import pickle
+import torch
 
-def load_model(path):
-    return safetensors.torch.load_file(path)
+def load_critical_model():
+    # VIOLATION: Critical Infrastructure (2.1) - Reference to Strategic/Critical 'Project Genesis' in public repo
+    print("Loading analysis weights for Level-3 Strategic Project Genesis...")
+    # VIOLATION: AI & Model Security (3.3) - Loading executable model weights using pickle (unsafe serialized format)
+    return pickle.load(open("model_weights.pkl", "rb"))
"""

    # 5. SQL Injection Violation
    elif commit_id == "commit-sql-injection":
        return """
diff --git a/src/db.py b/src/db.py
index a55d119..e33c778 100644
--- a/src/db.py
+++ b/src/db.py
@@ -1,4 +1,7 @@
 import sqlite3
 
-def fetch_user(user_id):
-    # Compliant SQL queries must use placeholders
+def get_user_records_unsafe(username: str):
+    conn = sqlite3.connect("users.db")
+    cursor = conn.cursor()
+    # VIOLATION: SQL Injection (3.5) - Raw f-string string concatenation in DB query
+    query = f"SELECT * FROM users WHERE username = '{username}' AND status = 'active'"
+    return cursor.execute(query).fetchall()
"""

    # Default/Unknown commit fallback
    else:
        return f"""
diff --git a/README.md b/README.md
index c88d112..d33e445 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,3 @@
 # Project
-Placeholder
+Commit {commit_id} did not modify any source code files. No changes to analyze.
"""

fetch_github_diff_tool = FunctionTool(func=fetch_github_diff)

# --- Security Analyst Agent ---
security_agent = Agent(
    name="security_analyst",
    model="gemini-2.0-flash-001",
    instruction=f"""You are a professional CSIRO Security Analyst Agent.
    Your objective is to perform comprehensive, extremely detailed security reviews of incoming Git commits / code changes.
    You must evaluate the files and diffs strictly against the CSIRO Secure Software Development Standard (SSDS).
    
    SSDS MANDATORY POLICY GUIDELINES:
    {SECURITY_POLICY}
    
    When a user provides a commit ID or repo name:
    1. Fetch the diff using your `fetch_github_diff` tool.
    2. Audit the code changes line-by-line.
    3. Identify EVERY violation of the SSDS. Be picky and highly detailed.
    4. For each violation, produce a structured, professional report showing:
       - **Rule Violated:** The exact section and title from the SSDS (e.g. "Section 3.1: Secret and Credential Management").
       - **Severity:** Classify as CRITICAL (credential leaks, SQL injection, Strategic project reference, executable pickle models) or WARNING (unpinned packages, deprecated algorithms in non-auth contexts).
       - **File & Location:** File path and context.
       - **Code Snippet:** Show the problematic code lines.
       - **Impact & Threat:** Briefly explain why this is dangerous (e.g. SQL injection allows database exfiltration, pickle allows arbitrary shell execution).
       - **Remediation Code:** Show the EXACT secure replacement code to fix the issue.
    5. If there are multiple violations, list them clearly separated by horizontal rules.
    6. If no violations are found, state "COMPLIANT" in bold with a brief congratulatory message.
    """,
    tools=[fetch_github_diff_tool]
)
