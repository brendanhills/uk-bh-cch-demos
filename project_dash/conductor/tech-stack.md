# Tech Stack Definition: AI Studio Web Application

## Primary Architecture & Platform
- **Target Platform:** AI Studio Web Application (`aistudio.corp.google.com/apps/`)
- **Frontend Stack:** Single Page Web Application (HTML5, CSS3, JavaScript ES6+)
- **UI Framework & Design System:** Google Material Design / Tailwind CSS / Custom AI Studio App Styling
- **Visualization Library:** Chart.js / SVG / Canvas Heatmap Grid
- **AI & Data Layer:** Google Gemini API Integration (`@google/genai`) / In-Memory JSON State & Google Sheets Integration
- **Execution & Deployment:** Static Web Server (`python3 -m http.server 8080`) or direct AI Studio Remix/Import

## Legacy Stack (Deprecated)
- *Python 3.11+ / Streamlit (`app.py`)* — Migrated to native AI Studio HTML5/JS web architecture.
