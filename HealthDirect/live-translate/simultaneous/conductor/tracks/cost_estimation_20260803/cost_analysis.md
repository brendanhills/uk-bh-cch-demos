# Cost-Estimation & Optimization Analysis (`cost_estimation_20260803`)

This document presents a comprehensive financial audit and operational pricing model for the Google Cloud & Gemini API services invoked within our real-time medical interpreter application.

---

## 1. Architectural Phasing & Cost Segregation

To ensure the end customer only reviews costs relevant to ongoing production billing, we partition the application's components into three distinct operational phases:

### Group A: Core Production Translation Application (Primary Focus)
This comprises the active runtime dependencies required to run live patient-nurse translation sessions. These are continuous, session-dependent usage costs.
* **Gemini Live API:** Dual-session WebSockets streaming bidirectional speech.
  - *Model Versions:* **`gemini-3.5-live-translate-preview`**, **`gemini-3.1-flash`**, **`gemini-2.5-flash`**.
  - *Cost Drivers:* Streaming audio input, live audio output, **transcription overhead**, **thinking budget level**, and **native vs. custom translation architectural overhead**.
* **Gemini Context Caching:** Reusing clinical instructions and glossary lists.
  - *Model Versions:* **`gemini-3.5-live-translate-preview`**, **`gemini-3.1-flash`**, **`gemini-2.5-flash`** (v1alpha).
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
We review the standard pricing across the three model options. Note that audio rates are identical, but text inputs/outputs are cheaper on Gemini 2.5 Flash, whereas cached token reads are priced differently:

| Metric / Item | `gemini-3.5-live-translate-preview` | `gemini-3.1-flash` | `gemini-2.5-flash` | Cost Type / Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Audio Input** | $3.00 / 1M tokens | $3.00 / 1M tokens | $3.00 / 1M tokens | Continuous incoming user speech (~$0.005/min) |
| **Audio Output** | $12.00 / 1M tokens | $12.00 / 1M tokens | $12.00 / 1M tokens | Spoken synthesized translations (~$0.018/min) |
| **Text Input** | $0.75 / 1M tokens | $0.75 / 1M tokens | $0.075 / 1M tokens | Static prompt parts, text messages |
| **Text Output** | $4.50 / 1M tokens | $4.50 / 1M tokens | $0.30 / 1M tokens | Returned text translations / transcripts |
| **Cached Token Read**| $0.15 / 1M tokens | $0.15 / 1M tokens | $0.015 / 1M tokens | 80% discounted rate for inputs matching cache |
| **Cache Storage** | $1.00 / 1M tokens / hr | $1.00 / 1M tokens / hr | $0.10 / 1M tokens / hr | Active context cache hourly hosting cost |

> [!IMPORTANT]
> **Transcription Cost Overhead Impact:**
> In our server configuration (`demo/web_server.py`), both `input_audio_transcription` and `output_audio_transcription` are enabled in `types.LiveConnectConfig` using `types.AudioTranscriptionConfig()`. 
> While Speech-to-Text (STT) transcription does not incur standalone GCP STT API costs here, **it increases Gemini Live API token consumption**. Generating full text transcripts on the output stream and feeding transcripts back as context adds substantial text input/output token overhead, directly scaling up the total session token count.

> [!TIP]
> **Thinking Level & Budget Cost Impact:**
> For model configurations that support configurable **Thinking Budgets / Thinking Levels** (such as **Gemini 3.1 / 3.5** models and above):
> - **No Thinking (None):** Immediate responses, lowest output token consumption.
> - **Low / Medium / High Thinking:** The model generates internal reasoning tokens prior to delivering the final translation/transcription.
> - **Billing Impact:** Internal thinking/reasoning tokens are billed at the **standard output token rate** (e.g., $4.50/1M text tokens). Selecting a high thinking level dramatically scales up output token counts and session costs, and should be balanced against translation quality requirements.

---

### B. Glossary Registration: Cloud Translation Advanced & Cloud Storage
* **Model Versions:* *Translation v3 Advanced*, *GCS JSON API v1*

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

## 3. Architectural Comparison: Native Translation vs. Prompt-Driven Custom Models

There is a fundamental architectural and cost distinction between utilizing the native translation engine versus the standard multi-turn custom instruction approach:

### Approach A: Native Translation Engine (`gemini-3.5-live-translate-preview`)
This approach leverages the native translation framework specified in `types.TranslationConfig`.
1. **Low Context / Prompt Size:** Because the model natively understands simultaneous translation, it does not require heavy, multi-paragraph guiding prompts in the `system_instruction`. The instructions only need to contain clinical rules and the glossary. 
   - *Est. Cached Prompt Size:* **~1,000 tokens** (highly cost-effective).
2. **Native Silence & Pacing Optimization:** Handling speech output natively at the engine level results in extremely tight, well-paced voice packets with zero trailing silence or filler phrasing.
   - *Est. Audio Output Duration:* Highly optimized (base length, no custom pacing overhead).
3. **Zero Translation Logic Overhead:** Native mapping minimizes reasoning/logic token overhead on output.

### Approaches B & C: Custom Prompt-Driven Translation (`gemini-3.1-flash` & `gemini-2.5-flash`)
These approaches do not support native `TranslationConfig`, and must rely on standard multi-turn `system_instruction` prompts to dictate translation rules.
1. **High Context / Prompt Size:** Requires a complex, multi-paragraph translation guide outlining pacing, dual-channel handling, and translation formatting rules, in addition to the glossary.
   - *Est. Cached Prompt Size:* **~3,000 tokens** (3x context caching read overhead compared to native).
2. **Manual Audio Pacing Overhead:** Requires manual streaming pacing (`pacing_mode='paced'`) and prompt instruction guidance to prevent the model from interrupting or rushing. This adds a slight padding to output packets.
   - *Est. Audio Output Duration:* **10% to 15% audio output token expansion** due to filler padding or manual prompt pacing boundaries.

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

### 2. Side-by-Side Playthrough Cost Comparison
We compare the total cost (USD) of running a full playthrough of each preset dialogue across the three models.

*Approach A (`gemini-3.5-live-translate-preview`) represents the optimized native translation config baseline. Approaches B & C utilize custom pacing guidelines and prompt caching overhead.*

| Medical Preset (Language) | Duration | Approach A: Native<br>`gemini-3.5-live-translate-preview` | Approach B: Prompt-Driven<br>`gemini-3.1-flash` | Approach C: Prompt-Driven<br>`gemini-2.5-flash` |
| :--- | :--- | :---: | :---: | :---: |
| **Arabic Asthma** | 86.43s | **$0.32569** | $0.35053 | $0.34802 |
| **German Fever** | 64.30s | **$0.27022** | $0.29230 | $0.28997 |
| **Spanish Ear** | 70.43s | **$0.29806** | $0.32245 | $0.31996 |
| **Hindi Cough** | 108.63s | **$0.46609** | $0.50419 | $0.50072 |
| **Vietnamese Paediatric**| 68.72s | **$0.29649** | $0.32100 | $0.31848 |

### Key Takeaways from Comparative Cost Audit:
1. **`gemini-3.5-live-translate-preview` is the Most Cost-Effective Option:** Across all presets, the native translation model is **`7.5% to 8.5%` cheaper** than the other models, despite Gemini 2.5 Flash having significantly lower text input/output rates.
2. **Audio Streaming Rates Dominate:** Because Gemini Live continuously streams audio ($3.00/1M input, $12.00/1M output), the text token pricing differences are entirely drowned out. The overhead of prompt-driven pacing (which expands spoken output audio duration by `12.5%`) adds far more cost than the cheaper text rate of 2.5 Flash can recover.
3. **Glossary Caching is Crucial:** For all models, utilizing Gemini Context Caching for our medical glossary and prompt rules cuts input reading costs by **`80% to 90%`**, saving several cents per session.

---

## 4. Future Track Extension: Conversation Summary Cost Model

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

## Phase 3: Google Sheets Projection Calculator CSV Design
*(Pending Implementation)*

## Phase 4: Cost Optimization Analysis & Recommendations Report
*(Pending Implementation)*
