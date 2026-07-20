---
name: customerize
description: Audit project for internal Google resources, infrastructure, and EAP/private preview services, recommending public cloud alternatives.
---

# Customerize Command (`/customerize`)

Audit source code and configuration files to identify internal Google dependencies, proprietary tools, and non-GA (EAP / Private Preview / Alpha) services, providing concrete recommendations for migrating to public Google Cloud or open-source equivalents.

## Audit Workflow

When the user runs `/customerize` (or asks to customerize a project/directory):

### 1. Scan for Internal Google Dependencies
Scan workspace files for:
- **Paths & Repos**: `google3/`, `//depot/`, `/cns/`, `/cfs/`, `/google/src/`, `/google/bin/`.
- **Internal Domains & Links**: `*.corp.google.com`, `go/` shortlinks, `b/` Buganizer references, `yaqs/`.
- **Internal Infrastructure & Tools**:
  - Build/VCS: `Blaze`, `Piper`, `Critique`, `Sponge`, `Flaze`.
  - Compute/Runtime: `Borg`, `Boq`, `Pod`, `Whitefly`.
  - RPC/Services: `Stubby`, `F1`, `S2`, `Monarch`, `Plx`, `Sherlog`.

### 2. Scan for EAP / Private Preview / Alpha Services
Scan for non-GA or restricted APIs:
- Import paths or package references containing `v1alpha`, `v1beta1`, `eap`, `private-preview`, `experimental`, or internal feature gates.
- Hardcoded internal GCP project IDs or internal endpoint overrides (e.g. `*.sandbox.google.com`, `internal-endpoint`).

### 3. Generate Audit Report & Migration Recommendations
Render a structured Markdown report formatted as follows:

```markdown
# 🛡️ Customerization & Public Migration Audit

## Summary
- **Files Scanned**: X
- **Internal Dependencies Found**: Y
- **EAP / Preview Features Found**: Z

## 📋 Audit Findings & Public Alternatives

| Category | Finding / Location | Current Usage | Recommended Public Alternative | Migration Complexity |
| :--- | :--- | :--- | :--- | :--- |
| Internal Path | `utils/io.py:L14` | `/cns/...` storage path | Google Cloud Storage (`gs://...`) | Low |
| Internal RPC | `client/api.py:L45` | Stubby RPC client | Standard gRPC / REST API | Medium |
| Private Preview | `config.py:L8` | `v1alpha1` API endpoint | Google Cloud GA Endpoint (`v1`) | Low |

## 🚀 Actionable Migration Steps
1. **Replace Internal Paths**: Replace local `/cns` or `/google/bin` references with standard cloud storage or environment variables.
2. **Update API Endpoints**: Migrate `v1alpha1` preview endpoints to standard GA (`v1`) public SDKs.
3. **Clean Proprietary Links**: Remove internal `go/` links or `b/` bug IDs in comments/docstrings.
```
