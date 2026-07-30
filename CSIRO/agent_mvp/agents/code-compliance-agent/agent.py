import os
import httpx
from google.adk import Agent
from google.adk.tools import FunctionTool

from urllib.parse import urlparse

def parse_github_repo(repo: str) -> str:
    """Parses a repository string or URL into 'owner/repo' format."""
    repo = repo.strip()
    parsed = urlparse(repo if "://" in repo else f"https://{repo}")
    if parsed.netloc in ("github.com", "www.github.com"):
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) >= 2:
            repo_name = parts[1][:-4] if parts[1].endswith(".git") else parts[1]
            return f"{parts[0]}/{repo_name}"
    if "/" in repo and not repo.startswith("http"):
        return repo
    return f"brendanhills-altostrat/{repo}"

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

# --- Dynamic Mock GitHub Tool ---
def fetch_github_diff(repo: str, commit_id: str) -> str:
    """Fetches a git diff for a given repo and commit ID.
    It first searches for physical files in the sample_pull_requests folder.
    If not found, it attempts to fetch the raw unified diff from the real GitHub API.
    If that fails or no token/access exists, it falls back to hardcoded mock content.
    """
    # 1. Try to load from physical sample_pull_requests directory
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_pull_requests")
    if os.path.exists(sample_dir):
        normalized_id = commit_id.replace("commit-", "pr-").replace("commit_", "pr_")
        possible_filenames = [
            f"{commit_id}.diff",
            f"{commit_id}",
            f"{normalized_id}.diff",
            f"{normalized_id}"
        ]
        for name in possible_filenames:
            file_path = os.path.join(sample_dir, name)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    pass

    # 2. Try to fetch from Real GitHub API
    owner_repo = parse_github_repo(repo)
    is_pr = commit_id.isdigit()
    if is_pr:
        url = f"https://api.github.com/repos/{owner_repo}/pulls/{commit_id}"
    else:
        url = f"https://api.github.com/repos/{owner_repo}/commits/{commit_id}"
        
    headers = {
        "Accept": "application/vnd.github.diff",
        "User-Agent": "CSIRO-Security-Compliance-Agent/1.0"
    }
    
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "dummy" not in token:
        headers["Authorization"] = f"token {token}"
        
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
    except Exception:
        pass # Fallback to mock data if connection fails

    # 3. Fallback Mock Data
    if commit_id in ["commit-safe", "pr-safe"]:
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

    elif commit_id in ["commit-secrets", "pr-secrets"]:
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

    elif commit_id in ["commit-dependencies", "pr-dependencies"]:
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

    elif commit_id in ["commit-ai-model", "pr-ai-model"]:
        return """
diff --git "a/scripts/inference.py" "b/scripts/inference.py"
index d22c118..e88d991 100644
--- "a/scripts/inference.py"
+++ "b/scripts/inference.py"
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

    elif commit_id in ["commit-sql-injection", "pr-sql-injection"]:
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

    else:
        return f"Unified diff for commit/PR ID '{commit_id}' on repository '{owner_repo}' could not be fetched from GitHub (or no local mock file was found). Check that the ID is valid and your GITHUB_TOKEN has access."

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
