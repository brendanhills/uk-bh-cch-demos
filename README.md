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

---

## Branch Guide & Presentation Modes

For customer presentations and demonstrations, use the following dedicated branches depending on the demo scenario required:

| Branch Name | Scenario / Purpose | Features & State |
| :--- | :--- | :--- |
| **`snapshot-of-psn-canberra-demo-with-instructions`** | **Pristine PSN Canberra Baseline** | The exact, verified stage demo presented at PSN Canberra. Focused on clinical concierge conversation, camera inspection of Leo Marlow discharge notes, nurse scheduling, and clean audio streaming without post-call modal interruptions. |
| **`feat/soap-controls`** / **`demo/psn-canberra-with-soap`** | **Clinical SOAP Export & Call Lifecycle** | Adds end-of-call lifecycle controls: 📞 End Call button, Header SOAP Note button, and automated clinical SOAP summary modal with one-click clipboard copy and print/EMR export. |

### Switching Between Demo Modes

```bash
# 1. Switch to pristine PSN Canberra stage demo:
git switch snapshot-of-psn-canberra-demo-with-instructions

# 2. Switch to SOAP-enabled demo:
git switch feat/soap-controls
# (or git switch demo/psn-canberra-with-soap)

# 3. Start or reload the agent server:
cd agent_demo
./run_demo.sh
```

