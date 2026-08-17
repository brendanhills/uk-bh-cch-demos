import os
import sys
import json
import logging
from typing import TypedDict, Optional, List, Dict, Any

from google import genai
from google.genai import types

logger = logging.getLogger('gemini_generator')

class ToneSynthesis(TypedDict):
    executive: str
    technical: str
    governance: str

class Top3Item(TypedDict):
    num: int
    type: str
    tag: str
    ref: str
    title: str
    impact: str
    action: str

class SleeperOutlier(TypedDict):
    ref: str
    title: str
    warning: str

class ExecutiveSynthesisResult(TypedDict):
    synthesis: ToneSynthesis
    top3: List[Top3Item]
    sleeperOutlier: SleeperOutlier
    generatedBy: str

class PodcastDialogueTurn(TypedDict):
    speaker: str
    role: str
    avatar: str
    time: str
    text: str

def get_gemini_client() -> Optional[genai.Client]:
    """Initializes genai.Client with ADC Vertex AI priority and API Key fallback."""
    project = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_REGION", "us-central1")
    
    # 1. Try Vertex AI with ADC if project is configured
    if project:
        try:
            return genai.Client(vertexai=True, project=project, location=location)
        except Exception as e:
            logger.warning(f"Vertex AI ADC initialization failed: {e}")

    # 2. Try API Key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "MY_GEMINI_API_KEY":
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"API Key Client initialization failed: {e}")

    # 3. Default ADC probe
    try:
        return genai.Client()
    except Exception as e:
        logger.error(f"Failed to initialize any Gemini client: {e}")
        return None

def build_synthesis_prompt(metrics: Dict[str, Any], gap_close_plans: List[Dict[str, Any]]) -> str:
    """Builds prompt string from metrics and plans."""
    prompt_template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "exec_summary_prompt.md")
    
    if os.path.exists(prompt_template_path):
        with open(prompt_template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        template = """You are the Principal Program Delivery Advisor for the leadership executive board.
Provide an exception-first executive briefing based on the following weekly metrics:
- Reporting Period: {{REPORT_WEEK}} (Ending {{REPORT_DATE}})
- Baseline: Compared against {{BASELINE_WEEK}} ({{BASELINE_DATE}})
- Overall Status: {{OVERALL_STATUS}}
- Commercial: {{COMMERCIAL_STATUS}}
- Milestone/IBR: {{IBR_STATUS}}
- ATO-C: {{ATO_STATUS}}
- Escalations: {{ESCALATIONS_COUNT}} items
- Active Plans: {{GAP_CLOSE_MOVEMENTS}}
- Total Risks: {{TOTAL_RISKS}}
- Inherent Avg: {{INHERENT_AVG_SCORE}} -> Residual Avg: {{RESIDUAL_AVG_SCORE}} (Delta {{DELTA_COMPRESSION}})
- Eventuated Issues: {{EVENTUATED_ISSUES_COUNT}} / Total Issues: {{TOTAL_ISSUES}}
"""

    plans_str = '\n'.join([
        f"- Plan #{p.get('num', idx+1)} ({p.get('ref', 'N/A')}) [{p.get('status', 'AMBER')}]: {p.get('title', '')} - Plan: {p.get('plan', '')} (Owner: {p.get('owner', 'TBD')}, Target: {p.get('target', 'TBD')})"
        for idx, p in enumerate(gap_close_plans)
    ])

    replacements = {
        "{{REPORT_WEEK}}": str(metrics.get('report_week', 'Week 28')),
        "{{REPORT_DATE}}": str(metrics.get('report_date', '14 Aug 2026')),
        "{{BASELINE_WEEK}}": str(metrics.get('baseline_week', 'Week 27')),
        "{{BASELINE_DATE}}": str(metrics.get('baseline_date', '07 Aug 2026')),
        "{{OVERALL_STATUS}}": str(metrics.get('overall_status', '🟡 AMBER (Stable)')),
        "{{COMMERCIAL_STATUS}}": str(metrics.get('commercial_status', '🟢 ON TRACK')),
        "{{IBR_STATUS}}": str(metrics.get('ibr_status', '🟡 DUE AUG 2026 (90%)')),
        "{{ATO_STATUS}}": str(metrics.get('ato_status', '🟢 GREEN')),
        "{{ESCALATIONS_COUNT}}": str(metrics.get('escalations_count', '5')),
        "{{GAP_CLOSE_MOVEMENTS}}": plans_str,
        "{{TOTAL_RISKS}}": str(metrics.get('total_risks', '107')),
        "{{INHERENT_AVG_SCORE}}": str(metrics.get('inherent_avg_score', '15.4')),
        "{{RESIDUAL_AVG_SCORE}}": str(metrics.get('residual_avg_score', '8.4')),
        "{{DELTA_COMPRESSION}}": str(metrics.get('delta_compression', '-7.0')),
        "{{EVENTUATED_ISSUES_COUNT}}": str(metrics.get('eventuated_issues_count', '21')),
        "{{TOTAL_ISSUES}}": str(metrics.get('total_issues', '29'))
    }

    prompt = template
    for key, val in replacements.items():
        prompt = prompt.replace(key, val)

    prompt += """

You MUST output your response strictly as valid JSON conforming to this schema:
{
  "synthesis": {
    "executive": "Exact 60-80 word single-paragraph executive summary highlighting posture, velocity, and key decisions.",
    "technical": "Exact 60-80 word single-paragraph engineering summary covering platform status, security assessors, and delivery milestones.",
    "governance": "Exact 60-80 word single-paragraph commercial and governance summary detailing escalations and milestone verification."
  },
  "top3": [
    {
      "num": 1,
      "type": "decision",
      "tag": "🚨 Immediate Executive Action",
      "ref": "Driver Ref e.g. 1.2b",
      "title": "Action item title",
      "impact": "Impact statement",
      "action": "Action description"
    },
    {
      "num": 2,
      "type": "schedule",
      "tag": "⚡ Critical Schedule Alignment",
      "ref": "Driver Ref e.g. 1.14",
      "title": "Schedule item title",
      "impact": "Impact statement",
      "action": "Action description"
    },
    {
      "num": 3,
      "type": "win",
      "tag": "🚀 Primary Delivery Win",
      "ref": "Driver Ref e.g. 1.10b",
      "title": "Delivery win title",
      "impact": "Impact statement",
      "action": "Action description"
    }
  ],
  "sleeperOutlier": {
    "ref": "Driver Ref e.g. 1.15",
    "title": "Deliverable name",
    "warning": "Rationale explaining why this green item is at risk of turning red due to schedule squeeze."
  }
}
"""
    return prompt

def generate_executive_synthesis(
    metrics: Dict[str, Any],
    gap_close_plans: List[Dict[str, Any]],
    model: str = "gemini-3.5-flash"
) -> Dict[str, Any]:
    """Generates structured executive decision synthesis using Gemini 3.5 Flash."""
    client = get_gemini_client()
    if not client:
        raise RuntimeError("Gemini Client could not be initialized. Please configure Google Cloud ADC or GEMINI_API_KEY in .env.")

    prompt = build_synthesis_prompt(metrics, gap_close_plans)
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    try:
        result = json.loads(response.text)
        result['generatedBy'] = model
        return result
    except Exception as e:
        logger.error(f"Failed to parse JSON output from Gemini: {e}\\nRaw response: {response.text}")
        raise ValueError(f"Invalid JSON output received from {model}: {e}")

def generate_multispeaker_podcast(
    metrics: Dict[str, Any],
    synthesis_result: Dict[str, Any],
    model: str = "gemini-3.5-flash",
    audio_out_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Generates dual-host dialogue transcript and multi-speaker audio."""
    client = get_gemini_client()
    if not client:
        raise RuntimeError("Gemini Client could not be initialized. Please configure Google Cloud ADC or GEMINI_API_KEY in .env.")

    prompt = f"""Generate a professional, high-impact 90-second conversational executive podcast briefing between two hosts:
- Alex (Host / Program Delivery Analyst, voice: Puck): Neutral, crisp, direct.
- Jordan (Co-Host / Technical Director, voice: Aoede): Authoritative, technical, solutions-focused.

Reporting Week: {metrics.get('report_week', 'Week 28')} ({metrics.get('report_date', '14 Aug 2026')})
Executive Summary: {synthesis_result.get('synthesis', {}).get('executive', '')}
Top 3 Attention Items: {json.dumps(synthesis_result.get('top3', []))}
Sleeper Outlier: {json.dumps(synthesis_result.get('sleeperOutlier', {}))}

Return STRICT JSON as an array of dialogue turns:
[
  {{"speaker": "Alex", "role": "Program Analyst", "avatar": "🎙️", "time": "0:00", "text": "Welcome to the Executive Briefing for {metrics.get('report_week', 'Week 28')}..."}},
  {{"speaker": "Jordan", "role": "Technical Director", "avatar": "🤖", "time": "0:18", "text": "Thank you Alex..."}}
]
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
    )

    try:
        script = json.loads(response.text)
        return script
    except Exception as e:
        logger.error(f"Failed to parse podcast script JSON: {e}")
        raise ValueError(f"Invalid podcast script JSON from {model}: {e}")
