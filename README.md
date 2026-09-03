# Cymbal Children's Hospital (CCH) Demos

This directory contains interactive healthcare AI prototypes developed for the **Cymbal Children's Hospital (CCH)** initiative:

---

## Available Demos

### 1. [Clinical Concierge Agent (`agent_demo/`)](agent_demo/README.md)
- **Technology**: Google Agent Development Kit (ADK), Gemini Live API (bidi multimodal streaming with native audio and vision), FastAPI, WebSockets.
- **Story**: An AI Clinical Concierge named *Jennie* that assists parents following hospital discharge. Supports real-time camera inspection of discharge papers, identity verification, nurse visit booking, and conversational reassurance.
- **Quick Start**:
  ```bash
  cd agent_demo
  ./run_demo.sh
  ```
- **Tests**:
  ```bash
  cd agent_demo
  uv run pytest
  ```

---

### 2. [Autonomous Surgical Co-Scheduler (`alphaevolve_scheduler/`)](alphaevolve_scheduler/README.md)
- **Technology**: Google AlphaEvolve evolutionary code mutation on Gemini Enterprise (`gemini-3.5-flash`), surgical staff scheduling simulation engine, interactive browser dashboard.
- **Story**: Demonstrates evolutionary algorithm generation optimizing Operating Theatre allocation and surgical staff schedules, increasing throughput from 122 to 152 patients while minimizing fatigue breaches.
- **Quick Start**:
  ```bash
  cd alphaevolve_scheduler
  ./serve.sh 9000
  ```
