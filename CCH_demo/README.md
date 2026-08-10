# Cymbal Children's Hospital (CCH) Demonstrations

This directory contains two complementary demonstration projects for Cymbal Children's Hospital:

---

## Sub-Projects

### 1. [`agent_demo/`](./agent_demo/)
**ADK Gemini Live API Multimodal Concierge Demo**
- **Description:** Real-time bidirectional streaming application using Google's Agent Development Kit (ADK) and Gemini Live API. Supports multimodal interactions (speech, text, documents) for patient check-in, triage, discharge summary generation, and voice concierge services.
- **Key Tech:** Python, ADK, FastAPI, WebSockets, Gemini Multimodal Live API.

### 2. [`alphaevolve_scheduler/`](./alphaevolve_scheduler/)
**Resource & Staff Co-Scheduling x AlphaEvolve**
- **Description:** Proof of Concept demonstrating AlphaEvolve evolutionary algorithm discovery for hospital resource, operating theatre (OT), and specialist staff co-scheduling. Features a 3-Phase executive storytelling dashboard, real-time candidate search feed, and dynamic disruption simulation.
- **Key Tech:** Python, AlphaEvolve, HTML5/CSS3/JS Gantt Dashboard, `uv`.

---

## Quick Start

### Running the AlphaEvolve Scheduler Demo
```bash
cd alphaevolve_scheduler
./serve.sh 9000
```
Then navigate to `http://localhost:9000/cch/`.

### Running the Live Agent Concierge Demo
```bash
cd agent_demo
./run_demo.sh
```
