# F-DSE Project Dashboard

An interactive dashboard application for the F-DSE Program.

## 🚀 Quick Start (Running on Port 9000)

### Option 1: AI Studio Single Page Web App (`index.html`)

If you are inside the `project_dash` directory:
```bash
uv run python -m http.server 9000
```

If you are in the workspace root directory:
```bash
uv run python -m http.server 9000 -d project_dash
```

Then open `http://localhost:9000` in your browser.

---

### Option 2: Streamlit Dashboard (`app.py`)

If you want to run the Streamlit application on port **9000**:

```bash
uv run streamlit run app.py --server.port 9000
```

---

## ⚡ AI Studio Import

1. Open **AI Studio App Builder** (`https://aistudio.corp.google.com/apps/`).
2. Create or remix an app draft.
3. Import `index.html` into your AI Studio workspace.
