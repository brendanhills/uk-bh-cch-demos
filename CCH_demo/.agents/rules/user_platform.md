# Chromebook / ChromeOS Invariants

1. **Chromebook Keyboard Shortcuts**:
   - Always reference ChromeOS keyboard shortcuts when asking the user to perform browser or OS actions:
     - **Hard Refresh / Bypass Cache**: `Ctrl + Shift + R` or `Ctrl + Refresh key (F3)`
     - **Open Developer Tools**: `Ctrl + Shift + I` or `Ctrl + Shift + J`
     - **Screenshot / Screen Snip**: `Ctrl + Show Windows (F5)` or `Ctrl + Shift + Show Windows`
     - **Clipboard**: `Ctrl + C` / `Ctrl + V` / `Search + V` (Clipboard history)
   - Do NOT reference macOS shortcuts (`Cmd + Shift + R`) or Windows key combinations unless explicitly requested.

2. **ChromeOS Hardware Context**:
   - Chromebook webcams default to 16:9 / 4:3 widescreen front cameras (`facingMode: "user"`).
   - Test and verify all web applications against standard Chrome browser rendering and touch/trackpad input.
