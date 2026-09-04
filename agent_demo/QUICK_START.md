# 🚀 Cymbal Children's Hospital (CCH) — Colleague Quick Start Guide

This guide contains everything you need to clone, set up, and run the **CCH Pediatric Home Care Concierge ("Jennie")** live streaming demo.

---

## 📋 1. Prerequisites

Before starting, ensure you have:
1. **Python 3.10+**
2. **uv** (Astral Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Google Cloud SDK (`gcloud`)** with access to a Google Cloud project with Vertex AI enabled.
4. **Google Chrome** (recommended for WebRTC/WebSocket audio and webcam streaming).

---

## ⚙️ 2. Setup & Installation

Run these commands in your terminal:

```bash
# 1. Clone the repository on the verified demo branch
git clone -b cch-agent-demo git@github.com:cloud-gtm/uk-bh-experiments.git
cd uk-bh-experiments/CCH_demo/agent_demo

# 2. Sync the Python virtual environment and dependencies
uv sync

# 3. Create your local .env configuration from the template
cp app/.env.example app/.env
```

### Configure `app/.env`:
Open `app/.env` in your editor and set your Google Cloud project details:
```dotenv
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

---

## 🔑 3. Authenticate & Launch

```bash
# Authenticate with Google Cloud Application Default Credentials (ADC)
gcloud auth application-default login

# Launch the demo server
./run_demo.sh
```

Once started, open your browser to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

When prompted by the browser, **allow Microphone and Camera access**.

---

## 📄 4. Document to Print for the Live Demo

* **File Location**: [`assets/discharge_notes_LeoMarlow.pdf`](assets/discharge_notes_LeoMarlow.pdf)
* **What to do**:
  - Print this single-page PDF (or open it full-screen on a tablet/phone).
  - During Phase 2 of the demo dialogue, hold this page up to your webcam so the model's multimodal camera scanner can inspect the patient discharge details.

---

## 🎬 5. Demo Walkthrough Script

For the full verbatim dialogue, refer to [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). Here is the quick 4-step sequence to speak into your microphone:

### **Phase 1: Greeting & Verification**
* **You**: *"G'day Jennie, hello there!"*
* **Jennie**: Welcomes you to Cymbal Children's Hospital and asks for your name and contact phone number.
* **You**: *"Hi Jennie, my name is Brendan Hills, and my phone number is 0412 345 678."*
* **Jennie**: Confirms your identity in the hospital system and asks how she can assist.

### **Phase 2: Document Camera Scan**
* **Action**: Hold the printed **Leo Marlow** discharge paper up to your webcam.
* **You**: *"We just brought Leo home from hospital. I'm holding up his discharge papers to the camera—could you review what's written here for me?"*
* **Jennie**: Scans the paper, verifies patient *Leo Marlow*, confirms diagnosis (*Acute Asthma Exacerbation*), medication (*Ventolin spacer & Prednisolone*), and follow-up plan.

### **Phase 3: Cost & NDIS Subsidy**
* **You**: *"I'd feel much better if a pediatric nurse could visit our home to check his breathing. How much does a home visit cost, and can we use our NDIS funding?"*
* **Jennie**: Quotes base rate ($150 AUD), calculates and applies a 15% NDIS subsidy discount ($127.50 out-of-pocket).

### **Phase 4: Home Care Nurse Booking**
* **You**: *"That sounds great, let's book Nurse Sarah for tomorrow morning."*
* **Jennie**: Books the appointment slot and updates the hospital EMR system.

---

## 🛠️ 6. Troubleshooting

- **Microphone / Audio Not Streaming**: Ensure Chrome has microphone permissions enabled for `http://127.0.0.1:8000`. Use headphones to avoid speaker loopback feedback.
- **Vertex AI Authentication Error**: Run `gcloud auth application-default login` again and confirm your user has `roles/aiplatform.user` on the configured GCP project.
- **Port Conflict**: If port 8000 is occupied, you can edit `./run_demo.sh` to change `--port 8000` to an alternate port like `--port 8080`.
