# Standalone Customization & Extension Architecture Guardrails

## 1. Global JSON Manifests are Ignored
In Standalone Jetski and Antigravity, the global declarative `skills.json`, `rules.json`, and `plugins.json` manifest files are exclusively designed for Workspace-level sharing (checked into Git via `.agents/`) and are **completely ignored** by the global discovery engine in `~/.gemini/config/`. 

## 2. Global Extensions Require Standalone Elements
To make customizations globally available, they MUST reside directly in their respective subdirectories as standalone items:
- **Global Skills**: Subdirectories in `~/.gemini/config/skills/<skill-name>/`
- **Global Rules**: `.md` files in `~/.gemini/config/rules/<rule-name>.md`
- **Global Plugins**: Subdirectories in `~/.gemini/config/plugins/<plugin-name>/` (and CLI `plugins/`)

## 3. Strict Non-Duplication Enforcement (Symlinks)
To honor the strict architectural constraint of "never making file copies" and avoiding out-of-sync duplicate files across repositories:
- NEVER copy or move extension files into `~/.gemini/config/`.
- ALWAYS use the Universal Customization Installer (`install.sh`) to automatically create **Symbolic Links (Symlinks)** in the global directories pointing exactly to the source files in the local repository.
