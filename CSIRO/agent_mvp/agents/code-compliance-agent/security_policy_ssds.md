# CSIRO Secure Software Development Standard (SSDS)

**Document Reference:** CSIRO-SEC-STD-2026.04  
**Version:** 2026.04  
**Status:** INTERNAL USE ONLY  
**Classification:** Restricted  
**Approved By:** CSIRO Technical Design Authority (TDA)  
**Last Reviewed:** May 2026  

---

## 1. Introduction and Purpose
This standard outlines the mandatory security requirements for software development and source code management across all CSIRO research business units, digital platforms, and software engineering initiatives. 

As a premier scientific research organisation, CSIRO encourages open collaboration; however, we must balance this open science paradigm with the strict protection of our intellectual property, proprietary partner data, and national security interests. This document provides an enforceable policy framework to ensure codebase integrity, prevent credential leakage, eliminate supply chain risks, and secure "Critical Infrastructure" and strategic research assets.

---

## 2. Classification-Based Repository Governance
Every software project within CSIRO must be classified according to its sensitivity. The project's classification dictates the permitted hosting environments, access controls, and release gates.

| Project Classification | Definition | Permitted Hosting Environments | External SaaS Exposure Rules |
| :--- | :--- | :--- | :--- |
| **Open Research (Level 1)** | General scientific inquiry with no commercial, proprietary, or national security sensitivities. Code intended for open-source publication. | GitHub (Public or Private), GitLab Public. | Permitted with pre-commit secret scanning. |
| **Standard Internal (Level 2)** | Proprietary operational tools, commercial-in-confidence research, client-funded projects, or internal-use administrative platforms. | CSIRO Enterprise GitLab, Enterprise GitHub (CSIRO Tenant). | External hosting strictly prohibited unless explicitly exempted by TDA. |
| **Strategic/Critical (Level 3)** | Projects designated as Critical Infrastructure, National Security interest, or containing high-value trade secrets (e.g., core quantum algorithms, advanced biosecurity software). | Air-gapped / Secure Internal Repositories with physical access logs. | **Strictly prohibited.** No external SaaS interaction, hosting, or metadata exposure. |

### 2.1 Critical Infrastructure Prohibitions & Requirements
Projects identified as **Strategic/Critical (Level 3)** must adhere to the following strict controls. Failure to do so constitutes a major security incident:
1. **Network Isolation:** Code and development environments must be hosted on physically isolated or high-assurance, air-gapped internal networks.
2. **Access Control:** Strict prohibition of external contributors, guest researchers, or third-party collaborators without formal, manual security clearance and vetting.
3. **Mandatory Sign-off:** A minimum of two-peer human code reviews and automated **"Security Agent" sign-off** is mandatory for all pull requests before code can be merged into active branches.
4. **Keyword Exclusion:** Any project references, names, or codenames of Level 3 strategic projects (such as "Project Genesis", "CSIRO-Quantum-Core") must never be committed to Level 1 or Level 2 repositories.

---

## 3. Secure Coding Requirements
All CSIRO codebases, regardless of their classification level, must adhere to these foundational secure coding principles during their design, development, and integration lifecycles.

### 3.1 Secret and Credential Management (Zero-Credential Policy)
The leakage of credentials is the leading cause of unauthorized access to CSIRO infrastructure.
1. **Zero Hardcoded Secrets:** No API keys, passwords, database connection strings, SSH private keys, symmetric cryptographic keys, or OAuth client secrets shall be hardcoded in any source code, configuration files, environment configuration templates, or documentation.
2. **Mandatory Scanning:** All commits and pushes to repository hosts must undergo server-side or pre-commit automated secret scanning using TDA-approved tooling (e.g., Snyk, Trufflehog, GitGuardian).
3. **Dynamic Injection:** Credentials must be injected at runtime using environment variables or retrieved from an approved Secret Management Platform (such as Google Cloud Secret Manager or HashiCorp Vault).

### 3.2 Supply Chain & Dependency Management
CSIRO must defend against software supply chain poisoning and malicious package takeovers.
1. **Vulnerability Scanning:** Developers must scan all third-party libraries, container images, and packages for known Common Vulnerabilities and Exposures (CVEs) before integration using approved tools (Snyk).
2. **Strict Version Pinning:** 
   *   **Prohibition of Wildcards & Latest Tags:** Developers must avoid using wildcard versions (e.g., `*`), dynamic ranges, or `"latest"` tags in dependency declarations (e.g., `requirements.txt`, `pyproject.toml`, `package.json`, Dockerfiles).
   *   **Exact Pinning:** All third-party dependencies must be strictly pinned to an exact, verified version number (e.g., `fastapi==0.110.0`) or, ideally, referenced by cryptographic content hash (SHA-256).
3. **Internal Mirrors:** Where available, dependencies should be pulled from CSIRO-hosted secure package mirrors rather than public package registries (PyPI, npm).

### 3.3 Artificial Intelligence & Model Security
In alignment with modern Information Security Manual (ISM) guidelines and AI safety protocols:
1. **Non-Executable Model Formats:** Machine learning and deep learning models (such as LLM weights, neural network checkpoints) must be stored and loaded in non-executable formats (e.g., **Safetensors** or ONNX) to prevent arbitrary code execution vulnerabilities associated with legacy serialized formats (such as PyTorch `.pt`, `.pth`, `.bin` files, or Python `pickle`).
2. **Data Isolation & Guardrails:** Organisational research data used for fine-tuning or prompt-engineering must reside in isolated tenants. Under no circumstances should CSIRO proprietary data be used to train or fine-tune public, external foundation models.

### 3.4 Cryptography & Data Protection
To prevent the compromise of encrypted research data:
1. **Insecure Algorithm Ban:** The use of broken or deprecated cryptographic algorithms (e.g., MD5, SHA-1, DES, RC4, Blowfish) for data encryption, digital signatures, or password hashing is strictly banned.
2. **Approved Algorithms:** Use AES-256 for symmetric encryption, RSA (minimum 2048-bit keys), or ECDSA (minimum 256-bit curves) for asymmetric encryption, and Argon2id or bcrypt for password hashing.

### 3.5 SQL Injection Prevention & Database Security
1. **No Raw SQL Concatenation:** Database queries must never be constructed using raw string formatting, string concatenation, or f-strings containing unescaped user input.
2. **Mandatory Parameterization:** All database queries must utilize parameterized queries, prepared statements, or an approved Object-Relational Mapper (ORM) library that automatically escapes user inputs.

---

## 4. Automated Enforcement & Audit Workflow
The CSIRO pipeline integrates the following automated checkpoints to enforce this standard:
1. **VS Code Assistance:** Developers use VS Code configured with Gemini Code Assist to receive real-time, secure coding suggestions.
2. **Git Commit Hooks:** Local pre-commit hooks prevent the inclusion of secrets or unpinned packages.
3. **Continuous Integration (CI) Security Gate:** Upon pushing to any repository branch, the CI/CD pipeline triggers an automated security audit utilizing a dedicated **Security Agent**.
4. **TDA Escalation:** If critical violations are detected in high-importance codebases, the Security Agent blocks the deployment and escalates the review to the Technical Design Authority (TDA).

---

## 5. Compliance, Exceptions, and Escalation
Any deviations from this standard must be formally documented, justified by research constraints, and approved by the CSIRO Technical Design Authority (TDA) before deployment.
*   **Non-Compliant Status:** Codebases failing to remediate critical violations within 7 business days will have their deployment privileges revoked.
