# Cost-Estimation & Optimization Analysis (`cost_estimation_20260803`)

This document presents a comprehensive financial audit and operational pricing model for the Google Cloud & Gemini API services invoked within our real-time medical interpreter application.

---

## 1. Architectural Phasing & Cost Segregation

To ensure the end customer only reviews costs relevant to ongoing production billing, we partition the application's components into three distinct operational phases:

### Group A: Core Production Translation Application (Primary Focus)
This comprises the active runtime dependencies required to run live patient-nurse translation sessions. These are continuous, session-dependent usage costs.
* **Gemini Live API:** Dual-session WebSockets streaming bidirectional speech.
  - *Model Versions:* **Gemini 3.5 Flash (Live Translate Preview)**, **Gemini 3.1 Flash (Live Preview)**.
  - *Cost Drivers:* Streaming audio input, live audio output, **transcription overhead**, and **thinking budget level**.
* **Gemini Context Caching:** Reusing clinical instructions and glossary lists.
  - *Model Versions:* **Gemini 3.5 Flash**, **Gemini 3.1 Flash** (v1alpha).
  - *Cost Drivers:* Hourly cache storage and hit token counts.

### Group B: Production Glossary Registration & Management (Secondary Focus)
This comprises the one-time or periodically run background ingestion tasks to compile and register HealthDirect term lists.
* **Cloud Translation Advanced:** Registering custom translation glossaries and validating medical terms.
  - *Model Version:* **Translation v3 Advanced** (Custom Glossary + Neural Machine Translation).
  - *Cost Drivers:* Character translations during glossary ingest.
* **Cloud Storage:** Hosting the compiled `glossary.csv` and `glossary.json` files.
  - *Model/API Version:* **GCS JSON API v1**.
  - *Cost Drivers:* Static standard storage (GB/month) and Class A/B API call counts.

### Group C: Dev-Time and Auxiliary Frameworks (Out of Scope for Production Billing)
These tools are used strictly by developers to generate offline synthetic conversation test files and run local verification sandboxes. **They do not contribute to live interpreter production costs.**
* **Cloud Text-to-Speech:** Synthesis of nurse and patient dialogue audio.
  - *Model Versions:* **Text-to-Speech v1** (utilizing **WaveNet** and **Neural2** high-fidelity voice engines).
* **Local Sandboxes:** Files like `test_prewarming_sandbox.py` or `compare_wav_with_script_gemini.py`.

---

## 2. Official Unit Pricing Rate Sheet (by Model Version)

### A. Core Translation App: Gemini Live API
* **Model Versions:** *Gemini 3.5 Flash / Gemini 3.1 Flash Live Preview* (Paid Tier, standard rates)

| Metric / Item | Pricing Unit Rate (USD) | Cost Type / Behavior |
| :--- | :--- | :--- |
| **Text Input** | $0.75 / 1 Million tokens | Static prompt parts, text messages |
| **Audio Input** | $3.00 / 1 Million tokens | Continuous incoming user speech (~$0.005 / minute) |
| **Text Output** | $4.50 / 1 Million tokens | Returned text translations |
| **Audio Output** | $12.00 / 1 Million tokens | Spoken synthesized translations (~$0.018 / minute) |
| **Context Cache Storage** | $1.00 / 1M tokens / hour | Active cache hourly hosting cost |
| **Cached Token Read** | $0.15 / 1 Million tokens | 80% discounted rate for inputs matching active cache |

> [!IMPORTANT]
> **Transcription Cost Overhead Impact:**
> In our server configuration (`demo/web_server.py`), both `input_audio_transcription` and `output_audio_transcription` are enabled in `types.LiveConnectConfig` using `types.AudioTranscriptionConfig()`. 
> While Speech-to-Text (STT) transcription does not incur standalone GCP STT API costs here, **it increases Gemini Live API token consumption**. Generating full text transcripts on the output stream and feeding transcripts back as context adds substantial text input/output token overhead, directly scaling up the total session token count.

> [!TIP]
> **Thinking Level & Budget Cost Impact:**
> For model configurations that support configurable **Thinking Budgets / Thinking Levels** (such as **Gemini 3.1 / 3.5 Flash and Pro** models and above):
> - **No Thinking (None):** Immediate responses, lowest output token consumption.
> - **Low / Medium / High Thinking:** The model generates internal reasoning tokens prior to delivering the final translation/transcription.
> - **Billing Impact:** Internal thinking/reasoning tokens are billed at the **standard output token rate** (e.g., $4.50/1M text tokens). Selecting a high thinking level dramatically scales up output token counts and session costs, and should be balanced against translation quality requirements.

---

### B. Glossary Registration: Cloud Translation Advanced & Cloud Storage
* **Model Versions:** *Translation v3 Advanced*, *GCS JSON API v1*

| Service | Operation | Unit Rate (USD) | Always Free Tier |
| :--- | :--- | :--- | :--- |
| **Cloud Translation Advanced v3** | Neural Machine Translation (NMT) | $20.00 / 1M characters | First 500,000 characters / month |
| **Cloud Translation Advanced v3** | Glossary Application / Hosting | $0.00 (Standard translation rate) | N/A |
| **Cloud Storage v1** | Standard Data Storage | $0.020 / GB / month | First 5 GB / month |
| **Cloud Storage v1** | Class A Operations (Upload, List) | $0.005 / 1,000 operations | First 5,000 operations / month |
| **Cloud Storage v1** | Class B Operations (Read, Fetch) | $0.0004 / 1,000 operations | First 50,000 operations / month |

---

### C. Dev-Time: Cloud Text-to-Speech
* **Model Versions:** *Text-to-Speech v1*

| Voice Tier | Price per 1 Million Characters | Always Free Tier |
| :--- | :--- | :--- |
| **WaveNet Voices** *(Nurse)* | $4.00 | First 4,000,000 characters / month |
| **Neural2 Voices** *(Patient)* | $16.00 | First 1,000,000 characters / month |

---

## 3. Future Track Extension: Conversation Summary Cost Model

As part of the upcoming **"Conversation Summary"** track, the application will compile the completed session transcript and generate a structured clinical SOAP note / summary. 

We model this future transaction utilizing standard, cost-efficient text-based Gemini models:
* **Model Version:** **Gemini 3.5 Flash (generate_content)**
* **Model pricing (Gemini 3.5 Flash Paid Tier):**
  - **Input Tokens:** $0.075 / 1 Million tokens
  - **Output Tokens:** $0.300 / 1 Million tokens

### Projected Summary Costs per Session (Example):
For a standard 15-minute dialogue (approx. 3,000 words / ~4,000 tokens input, and ~800 tokens output):
* **Input cost:** 4,000 input tokens * $0.000000075 / token = $0.00030 USD
* **Output cost:** 800 output tokens * $0.000000300 / token = $0.00024 USD (Assuming **No Thinking / Low Thinking** model settings)
* **High Thinking Overhead Adjustment:** If standard summary generation utilizes a high thinking level (e.g. adding 1,500 thinking tokens for clinical clinical validation), output tokens increase to 2,300 tokens:
  - *Adjusted Output Cost:* 2,300 output tokens * $0.000000300 / token = $0.00069 USD
* **Total Summary Cost per Session:** **$0.00054 USD to $0.00099 USD** (approx. 1/10th of a cent)

---

## Phase 2: Dialogue Token Audit & Empirical Cost Calculations

To establish a concrete, empirical baseline of translation costs, we audited the actual clinical dialogue scripts and high-fidelity stereo WAV files inside the `samples/` directory.

### 1. Dialogue Script & Audio Audit
Below are the exact measurements of speech duration, conversational turns, word count, and estimated Gemini Live tokenization bounds for each medical dialogue preset. 

*Audio is tokenized at Gemini’s standard audio density of **250 tokens per second** (1 token per 4ms of audio).*

| Medical Preset (Language) | Conversation WAV File | Playthrough Duration | Dialogue Turns | Nurse Word Count (English) | Patient Word Count (Foreign) | Est. Audio Input Tokens (Both Channels) | Est. Audio Output Tokens (Translations) |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **Arabic Asthma** | `ar_asthma_session.wav` | 86.43s (1.44m) | 7 | 88 words | 56 words | 43,215 tokens | 16,160 tokens |
| **German Fever** | `de_fever_session.wav` | 64.30s (1.07m) | 6 | 71 words | 58 words | 32,150 tokens | 14,320 tokens |
| **Spanish Ear** | `es_ear_session.wav` | 70.43s (1.17m) | 6 | 83 words | 59 words | 35,215 tokens | 15,860 tokens |
| **Hindi Cough** | `hi_cough_session.wav` | 108.63s (1.81m) | 6 | 120 words | 106 words | 54,315 tokens | 25,000 tokens |
| **Vietnamese Paediatric** | `vi_paediatric_session.wav` | 68.72s (1.15m) | 6 | 67 words | 79 words | 34,360 tokens | 15,940 tokens |

---

### 2. Empirical Playthrough Cost Breakdown
Using the official model rates, we calculate the precise sub-penny costs incurred for running a single full playthrough of each preset dialogue. This includes input audio streaming, translated spoken audio output, live transcription text token output, and glossary context cache reads:

| Cost Category | ARABIC Preset | GERMAN Preset | SPANISH Preset | HINDI Preset | VIETNAMESE Preset |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Audio Input Cost** *(Streaming)* | $0.12965 | $0.09645 | $0.10565 | $0.16295 | $0.10308 |
| **2. Audio Output Cost** *(Spoken Trans)* | $0.19392 | $0.17184 | $0.19032 | $0.30000 | $0.19128 |
| **3. Text Output** *(Transcription Overhead)* | $0.00183 | $0.00163 | $0.00180 | $0.00285 | $0.00183 |
| **4. Cache Read Cost** *(Glossary Priming)* | $0.00090 | $0.00090 | $0.00090 | $0.00090 | $0.00090 |
| **👉 TOTAL PLAYTHROUGH COST (USD)** | **$0.32629** | **$0.27082** | **$0.29866** | **$0.46669** | **$0.29709** |
| **👉 TOTAL PLAYTHROUGH COST (AUD)** | **$0.49438** | **$0.41033** | **$0.45252** | **$0.70711** | **$0.45014** |

*(AUD converted at an indicative exchange rate of 1 USD = 1.515 AUD).*

### Core Takeaways from Empirical Audit:
1. **Audio Output is the Major Cost Driver:** Due to the higher output rate of $12.00/1M tokens, the spoken synthesized translations generated by the models represent approximately **55% to 65% of the total session costs**.
2. **Streaming Audio Input is a Close Second:** Streaming dual audio feeds simultaneously represents **35% to 40% of the cost**.
3. **Transcription Text Output is Negligible:** While `AudioTranscriptionConfig` adds output stream text overhead, text is priced at only $4.50/1M tokens, meaning the visual transcription layer costs less than **1% of the total session cost** (approx. 1/5th of a cent per playthrough). This is an incredibly favorable trade-off for accessibility and clinical logging.

---

## Phase 3: Google Sheets Projection Calculator CSV Design
*(Pending Implementation)*

## Phase 4: Cost Optimization Analysis & Recommendations Report
*(Pending Implementation)*
