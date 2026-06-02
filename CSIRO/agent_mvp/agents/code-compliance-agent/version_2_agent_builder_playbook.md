# Version 2: Google Cloud Vertex AI Agent Builder (Playbook/Low-Code Agent)

This document outlines the detailed instructions and blueprints to construct the CSIRO Security Compliance Assistant in **Google Cloud Vertex AI Agent Builder** as a **Playbook-based (Low-Code) Agent**.

---

## 🏗️ Setup Instructions in Vertex AI Agent Builder
1. Go to the **Google Cloud Console** -> **Vertex AI Agent Builder**.
2. Click **Create Agent** and select **Playbook** (formerly Chat/Playbook-based).
3. Name your agent: `security_policy_compliance_assistant`.
4. Choose the default language (`en`) and region (`us-central1` or your preferred region supporting Generative Playbooks).
5. Link your grounding **Data Store** (containing `security_policy_ssds.md` or `Secure Software Development Standard (SSDS).pdf`).
6. Set the primary generative model (e.g., `gemini-1.5-pro` or `gemini-2.0-flash`).
7. Paste the **Playbook Goal and Steps** (System Instructions) below into the **Instructions** or **Goal** panel.

---

## 📝 Playbook Goal & Steps

```text
- **Goal**: You are the CSIRO Security compliance agent. Your objective is to audit incoming repository code changes (diffs) against the CSIRO Secure Software Development Standard (SSDS) to determine if any changes require a Manual Human-in-the-Loop Security Check, taking into account any approved active waivers.

- **Steps**:
  1. Greet the developer and ask them to provide the GitHub **Repository Name** and **Commit ID** (or Pull Request branch) to analyze.
  2. Call the tool ${tool:Get_Repository_Diff} with the provided 'repo' and 'commit_id' to retrieve the Git diff content.
  3. Call the tool ${tool:Lookup_Exceptions_Registry} with the 'repo' to fetch active, approved Technical Design Authority (TDA) security waivers for that repository.
  4. Perform a line-by-line audit of the retrieved Git diff against the Secure Software Development Standard (SSDS) document grounded in your attached Data Store. Focus on:
     - Section 3.1: Zero-Credential Policy (hardcoded secrets).
     - Section 3.4: Cryptography Standard (broken hashing/encryption like MD5/SHA-1).
     - Section 3.2: Supply Chain (exact package version pinning).
     - Section 3.3: AI Model Security (executable formats like pickle/PyTorch legacy loaders).
     - Section 3.5: SQL Injection Prevention (f-string concatenation in DB queries).
     - Section 2.1: Project Classification (mention of strategic projects like "Project Genesis" in low-sensitivity repos).
  5. For any policy violation found, cross-reference it with the list of waivers retrieved from ${tool:Lookup_Exceptions_Registry}:
     - If an active waiver covers the violation (e.g., a waiver for legacy MD5 is active and hasn't expired), mark that violation as "WAIVED - COMPLIANT" in your output and display the approved justification.
     - If no waiver exists (or if it is expired), classify it as a "CRITICAL VIOLATION" or "WARNING" and provide remediation.
  6. Output a detailed compliance audit report in clear, structured Markdown:
     - Clearly separate multiple violations using horizontal dividers.
     - Provide the exact file, line number, problematic snippet, impact, and compliant remediation code blocks.
  7. If there are no violations (or all violations are covered by active waivers), output a bold "**COMPLIANT**" status with a congratulatory note.
```

---

## 🔧 Tool Configuration Mappings

To connect this playbook to our live local API or standard deployed endpoints, add the following two custom OpenAPI tools:

### Tool 1: Get_Repository_Diff
- **Type**: `OpenAPI`
- **Spec Source**: Copy and paste the contents of [get_repository_diff_spec.yaml](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/tools_openapi_specs/get_repository_diff_spec.yaml) into the YAML editor in the Tools section.
- **Description**: "Fetches raw unified git diffs for a repository and commit ID to check line-by-line compliance."

### Tool 2: Lookup_Exceptions_Registry
- **Type**: `OpenAPI`
- **Spec Source**: Copy and paste the contents of [lookup_exceptions_spec.yaml](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/tools_openapi_specs/lookup_exceptions_spec.yaml) into the YAML editor in the Tools section.
- **Description**: "Queries the central database for active approved security waivers (TDA exceptions) linked to a specific repository."

---

## 📂 Data Store Grounding Settings
1. Create a **Search Data Store** inside Vertex AI Agent Builder.
2. Select **Cloud Storage** or **File Upload** and upload `/home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/security_policy_ssds.md` (or the corresponding PDF).
3. Name the Data Store: `csiro_ssds_security_policy`.
4. Link this Data Store to the `security_policy_compliance_assistant` playbook under the **Data Stores** tab.
5. This grounds the LLM’s reasoning, ensuring it quotes exact rules (like Section 3.1 or Section 3.3) accurately and doesn't hallucinate policies.
