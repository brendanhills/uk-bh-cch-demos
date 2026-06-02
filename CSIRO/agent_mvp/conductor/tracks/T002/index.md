# Track T002: Agent Designer (No-Code Prompt Version)

## Status
- **Status:** ✅ COMPLETED
- **Owner:** CSIRO Security Engineering Team

## Objectives
Create a highly detailed, professional compliance-aware system prompt and few-shot testing suite to construct the CSIRO Code Compliance Assistant in Google Cloud's visual Agent Designer as a single-step no-code agent.

## Implementation Details
1. **Core Prompt System:**
   - Define exact line-by-line evaluation rules against the CSIRO Secure Software Development Standard (SSDS).
   - Enforce check constraints for:
     - Section 3.1: Zero-Credential policy.
     - Section 3.4: Insecure cryptographic algorithms (MD5, SHA-1).
     - Section 3.2: Dependency pinning.
     - Section 3.3: AI model file-format loading (Safetensors vs executable pickle/pt).
     - Section 3.5: SQL Injection query parameterized execution.
     - Section 2.1: Critical Strategic project exposure ("Project Genesis").
2. **Few-Shot Validation Suite:**
   - Provide concrete examples of compliant vs non-compliant diff payloads to ensure high-accuracy reasoning in the Agent Designer Preview simulator.
   - Enforce exact markdown audit reporting formats with side-by-side impact explanation and remediation code blocks.

## Checklist
- [x] Create core role instructions and evaluation workflow rules.
- [x] Create few-shot examples for hardcoded secrets, insecure hashes, and SQL injections.
- [x] Deliver copy-pasteable prompts file `agents/code-compliance-agent/version_1_agent_designer_prompts.md`.
