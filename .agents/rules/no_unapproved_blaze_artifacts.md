# Blaze Artifact Creation Policy

**MANDATORY RULE**: Do **NOT** create Blaze or Bazel artifacts unless the user explicitly requests or approves it.

## Guidelines
1. **No BUILD Files**: Do not author `BUILD` or `BUILD.bazel` files in standalone workspaces, Antigravity plugins, or open-source projects without explicit user approval.
2. **No `*_main.py` Wrapper Splits**: Do not split Python scripts into separate library (`foo.py`) and entrypoint wrapper (`foo_main.py`) files. Author standard Python files that contain executable `if __name__ == '__main__':` entrypoints.
3. **Standalone First**: All scripts, tests, and skills must function out of the box using standard Python 3 runtime tooling (`python3`, `unittest`, `pytest`) without depending on Blaze/Bazel targets.
