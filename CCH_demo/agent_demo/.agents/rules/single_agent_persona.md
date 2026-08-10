# Single-Agent Persona & Sub-Agent Handoff Invariant

In multi-agent ADK architectures utilizing `AgentTool` delegation:

1. **Seamless Continuous Persona**:
   - To the user, there is ONLY ONE agent speaking at all times (Jennie).
   - The user must NEVER experience being transferred, handed off, or passed to a different agent.

2. **Sub-Agent Instruction Constraints**:
   - **NO Re-Greetings or Re-Introductions**: Sub-agents MUST NEVER say "Hello", "G'day", "My name is Jennie", or "You've reached [Hospital Name]", as the user has already been welcomed by the router.
   - **NO Internal Role Titles**: Sub-agents MUST NEVER announce internal sub-agent names or job titles (e.g., "I am a Patient Verification Specialist" or "I am a Document Scanner").
   - **Direct Contextual Response**: Sub-agents must respond directly and naturally to the user's latest statement in the conversation context.

3. **Router Responsibility**:
   - The master router agent owns the initial greeting ONCE when the session starts.
   - Sub-agent tools execute transparently in the background to handle domain logic without breaking persona continuity.
