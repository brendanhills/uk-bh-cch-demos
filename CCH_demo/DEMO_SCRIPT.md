# 🏥 Cymbal Children's Hospital (CCH)
## Home Care Concierge — Live Demonstration & Testing Script

This script document outlines the end-to-end dialogue, technical tool calls, and visual workflow for demonstrating the **CCH Home Care & Support Specialist ("Jennie")** web application. It is based on the transcript and verified fixes from the latest live audio streaming test.

---

## 1. ⚙️ Test & Demo Overview

| Property | Details |
| :--- | :--- |
| **Agent Persona** | **Jennie** — Home Care & Support Specialist at Cymbal Children's Hospital (CCH) |
| **Voice & Tone** | Authentic Australian English (`en-AU`), warm, clinical, empathetic, and professional |
| **Presenter / Parent** | **Brendan** (Father of pediatric asthma patient **Leo Marlow**) |
| **Hardware Setup** | Directional Lapel Mic with continuous live audio streaming (no Push-To-Talk) |
| **Primary Model** | `gemini-2.5-flash-native-audio` (Vertex AI / Live API streaming) |
| **Backend / Tools** | Python ADK + FastAPI + 6 CCH Clinical & Financial Tools + EMR Integration |

---

## 2. 🛡️ Verified Guardrails & Bug Fixes Included in Script

1. **Strict Initial Engagement (BUG-15 Fix):** Agent waits for parent to open conversation, delivers exact mandatory greeting, and confirms identity/phone before proceeding—without demanding discharge paperwork prematurely.
2. **Name Persistence & Child Terminology:** Once Brendan identifies himself, Jennie addresses him as "Brendan" in every subsequent turn and refers to "your child / Leo".
3. **Visual Document Scan & Debug Print (BUG-9 Fix):** Jennie scans the discharge papers on camera, logs extracted text for session transcript, and checks for multi-page indicators without hallucinating pages.
4. **Financial Subsidy Threshold Rules:** Jennie checks approval limits (subsidies $\le 20\%$ approved directly; $> 20\%$ flagged for supervisor sign-off).
5. **EMR Sync:** Automatically logs visit details, approved subsidies, and clinical notes to EMR record `P-CCH-883012`.
6. **Lapel Mic Audio Stream:** Tested on continuous audio mode without PTT fragmentation or false room chatter interruptions.

---

## 3. 🎬 Step-by-Step Verbatim Dialogue Script

### **Phase 1: Stream Connection & Initial Engagement**

**Action:** Presenter opens `http://localhost:8000`, verifies microphone access, and clicks **Start Stream**. Indicator turns green (**Connected**).

```text
[Speaker: Brendan]
"G'day Jennie, hello there!"

[Speaker: Jennie (Agent)]
"Thank you for visiting Cymbal Children's Hospital. My name is Jennie. I'm here to assist you with the home care, discharge plan and guide you in the right direction. Just to confirm who am I speaking with and your phone number so that I can look into the system."

[Speaker: Brendan]
"Hi Jennie, my name is Brendan Hills, and my phone number is 0412 345 678."

[Speaker: Jennie (Agent)]
"G'day Brendan! Thank you for confirming those details. It's lovely to speak with you today. How can I assist you and your child with home care or discharge support today?"
```

---

### **Phase 2: Discharge Paperwork Visual Scan & Guidance**

**Action:** Brendan holds up Leo's printed discharge paper to the webcam.

```text
[Speaker: Brendan]
"We just brought Leo home from CCH after his asthma admission. I'm holding up his discharge papers to the camera—could you review what's written here for me?"

[Speaker: Jennie (Agent)]
"I can see those discharge papers clearly on the camera, Brendan. Let me read through what's printed here:

- Patient: Leo Marlow
- Diagnosis: Acute Asthma Exacerbation
- Discharge Medications: Salbutamol (Ventolin) inhaler via spacer (2 puffs every 4 hours as needed) and a 3-day course of oral prednisolone.
- Follow-up: Local GP check within 5 days, and monitor breathing closely.

Everything looks clear and complete on this page. Leo's care plan focuses on regular spacer technique and keeping his airways clear. Are there any specific questions you have about his medications or setting up a nurse visit at home?"
```

---

### **Phase 3: Home Care Cost Estimation & NDIS Subsidy Approval**

```text
[Speaker: Brendan]
"I'd feel much better if a pediatric nurse could come to our home to check his breathing and review his spacer technique. How much does a home visit cost, and can we use our NDIS funding?"

[Speaker: Jennie (Agent)]
"I completely understand, Brendan. Having a nurse visit at home provides great peace of mind. Let me generate a cost estimate for a specialized pediatric nurse home visit for you."
```

🛠️ **System Call:** `get_home_care_cost_estimate(number_of_visits=1, service_type="Pediatric Nurse Visit")`
> **Response:** Total base cost = `$150.00 AUD` (pre-subsidy).

```text
[Speaker: Jennie (Agent)]
"The base rate for a specialized pediatric nurse home visit is $150 AUD. Regarding NDIS, yes! We can apply your pediatric NDIS package. I can approve and register a standard 15% NDIS funding subsidy onto Leo's support plan right away. Let me process that approval for you now."
```

🛠️ **System Call:** `approve_funding_subsidy(subsidy_type="NDIS", requested_rate=0.15)`
> **Response:** `approved = True`, message: *"Successfully approved NDIS subsidy rate of 15%."*

🛠️ **System Call:** `apply_subsidy_to_support_plan(subsidy_type="NDIS", approved_rate=0.15, support_plan_id="SP-CCH-9921")`
> **Response:** `status = "Applied"`, message: *"Registered NDIS subsidy at 15% onto support plan SP-CCH-9921."*

```text
[Speaker: Jennie (Agent)]
"Great news, Brendan. I've officially approved and applied a 15% NDIS subsidy to Leo's home care support plan, reducing your out-of-pocket cost. Now let's find an available time slot for Nurse Sarah or Nurse Michael to visit."
```

---

### **Phase 4: Nurse Visit Appointment Scheduling**

```text
[Speaker: Brendan]
"That's wonderful news. Can we schedule a visit for tomorrow?"

[Speaker: Jennie (Agent)]
"Let me check our clinical schedule for open nurse visit slots tomorrow."
```

🛠️ **System Call:** `get_available_support_times(requested_date="tomorrow", service_type="Pediatric Nurse Visit")`
> **Response:** Slots available:
> - `slot_1`: 09:00 AM (Nurse Sarah)
> - `slot_2`: 11:30 AM (Nurse Michael)
> - `slot_3`: 02:00 PM (Nurse Sarah)
> - `slot_4`: 04:30 PM (Nurse Michael)

```text
[Speaker: Jennie (Agent)]
"We have four open slots tomorrow, Brendan: 9:00 AM with Nurse Sarah, 11:30 AM with Nurse Michael, 2:00 PM with Nurse Sarah, and 4:30 PM with Nurse Michael. Which time suits your schedule best?"

[Speaker: Brendan]
"The 9:00 AM slot with Nurse Sarah would be perfect."

[Speaker: Jennie (Agent)]
"Excellent choice. Let me confirm and book that 9:00 AM appointment for Leo now."
```

🛠️ **System Call:** `schedule_home_care_visit(date="tomorrow", time="09:00 AM", child_name="Leo Marlow", parent_name="Brendan Hills", service_type="Pediatric Nurse Visit")`
> **Response:** `booking_status = "Confirmed"`, `booking_id = "B-CCH-84291"`, `assigned_practitioner = "Nurse Sarah"`.

```text
[Speaker: Jennie (Agent)]
"All booked! Nurse Sarah is confirmed to visit Leo tomorrow morning at 9:00 AM. Confirmation ID: B-CCH-84291. Nurse Sarah will conduct a full respiratory assessment, check his oxygen levels, and go over his Ventolin spacer technique with you."
```

---

### **Phase 5: Hospital EMR Record Sync & Closing Guidance**

```text
[Speaker: Brendan]
"Thank you so much Jennie, that's a huge relief."

[Speaker: Jennie (Agent)]
"It's my absolute pleasure, Brendan. To ensure Leo's full medical team stays aligned, I am updating his hospital EMR record right now."
```

🛠️ **System Call:** `update_hospital_emr(child_name="Leo Marlow", booked_visits=["Confirmed Nurse Sarah tomorrow 09:00 AM (B-CCH-84291)"], approved_subsidies=[{"type": "NDIS", "rate": 0.15}], clinical_notes="Parent Brendan confirmed. Discharge papers reviewed for Acute Asthma Exacerbation. Ventolin spacer review requested. 15% NDIS subsidy applied. Nurse visit booked.")`
> **Response:** `emr_update_status = "Success"`, `patient_id = "P-CCH-883012"`.

```text
[Speaker: Jennie (Agent)]
"Everything is logged in Leo's CCH medical file under patient ID P-CCH-883012. 

Please remember, Brendan: if you notice Leo showing signs of severe distress—such as chest retractions, rapid breathing, or grunting—do not wait for tomorrow's visit. Bring him directly to our 24/7 Cymbal Children's Hospital Emergency Department or call 000 immediately.

You're doing a fantastic job caring for Leo. Is there anything else I can help you with today?"

[Speaker: Brendan]
"No, that covers everything. Thank you Jennie!"

[Speaker: Jennie (Agent)]
"No worries at all, Brendan! Have a wonderful day and give Leo our best. Cheerio!"
```

---

## 4. 📊 Technical Tool Call Summary Matrix

| Step | Tool Name | Core Inputs | Expected Return |
| :--- | :--- | :--- | :--- |
| **1** | `get_home_care_cost_estimate` | `number_of_visits=1` | Base Cost: `$150.00 AUD` |
| **2** | `approve_funding_subsidy` | `subsidy_type="NDIS"`, `requested_rate=0.15` | `approved=True` |
| **3** | `apply_subsidy_to_support_plan` | `subsidy_type="NDIS"`, `approved_rate=0.15` | `status="Applied"`, Plan `SP-CCH-9921` |
| **4** | `get_available_support_times` | `requested_date="tomorrow"` | Available slots (09:00 AM, 11:30 AM, 02:00 PM, 04:30 PM) |
| **5** | `schedule_home_care_visit` | `date="tomorrow"`, `time="09:00 AM"`, `child_name="Leo Marlow"`, `parent_name="Brendan Hills"` | `booking_id="B-CCH-84291"`, Practitioner: Nurse Sarah |
| **6** | `update_hospital_emr` | `child_name="Leo Marlow"`, `booked_visits`, `approved_subsidies`, `clinical_notes` | `emr_update_status="Success"`, Patient ID: `P-CCH-883012` |

---

## 5. 📋 Pre-Demo Verification Checklist

- [x] Backend server running (`uvicorn main:app --host 0.0.0.0 --port 8000`)
- [x] Environment credentials configured in `app/.env` (`GEMINI_API_KEY` or Vertex AI `GCP_PROJECT`/`GCP_LOCATION`)
- [x] Directional lapel mic selected in browser audio input settings
- [x] Physical or digital copy of CCH Discharge Paperwork ready for camera presentation
- [x] Verify speaker volume and browser Web Audio playback
