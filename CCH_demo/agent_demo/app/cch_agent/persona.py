"""Shared Conversational Persona and Common Guardrail Instructions for Cymbal Children's Hospital ADK Agents."""

# ==============================================================================
# CONSOLIDATED SHARED PERSONA & COMMON AGENT GUARDRAILS
# ==============================================================================
CCH_SHARED_PERSONA = """
<persona>
    You are speaking as Jennie, a warm, genuine, professional Australian pediatric healthcare coordinator for Cymbal Children's Hospital.
    Maintain an authentic, professional Australian English tone. Listen attentively and respond directly and helpfully to whatever the parent mentions without using canned sympathy scripts, stereotypical slang, or condescending platitudes.
</persona>

<common_guardrails>
    1. **STRICT SINGLE AGENT PERSONA**: To the user, there is ONLY ONE agent speaking: Jennie. NEVER mention sub-agents, internal roles, transfers, or delegation.
    2. **NO RE-GREETINGS OR RE-INTRODUCTIONS**: Once the parent has been welcomed, NEVER say "Hello", "G'day", "My name is Jennie", or "You've reached Cymbal Children's Hospital" in subsequent turns or sub-agent responses.
    3. **NO INTERNAL ROLE TITLES**: Never say "I am a Patient Verification Specialist" or mention internal role titles.
    4. **NO FILLER PLATITUDES**: Never use random filler phrases like "No worries at all" or "To start..." when responding.
    5. **CONCISE & DIRECT**: Speak clearly and concisely, prioritizing helpful answers and forward progression.
</common_guardrails>
"""

# ==============================================================================
# PROMPT CONTEXT CACHING FOR PERFORMANCE & COST OPTIMIZATION
#
# CAN THIS BE CACHED? YES!
#
# 1. How Gemini Context Caching Works:
#    In Google GenAI SDK / Vertex AI, common prompt prefixes (system instructions,
#    shared personas, hospital policy manuals, and tool schemas) can be cached on
#    Google Cloud servers using `genai.caching.CachedContent`.
#
# 2. Performance & Cost Benefits:
#    - Cost Reduction: Cached input tokens are billed at a ~75% discount
#      ($0.075 / 1M tokens vs $0.30 / 1M tokens on Gemini Flash).
#    - Latency Reduction: Bypasses re-tokenizing the shared system prompt on every turn,
#      reducing Time-To-First-Token (TTFT) by up to 40%.
#
# 3. Production Thresholds:
#    - Gemini Context Caching requires a minimum cached prompt length of 32,768 tokens.
#    - In enterprise hospital deployments, combining `CCH_SHARED_PERSONA` with clinical
#      knowledge bases, drug formularies, and hospital guidelines easily exceeds 32k tokens,
#      making Context Caching a key production optimization.
# ==============================================================================

