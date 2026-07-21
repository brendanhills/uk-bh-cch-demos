# Implementation Plan - Transition to Global Rule with SQLite Metrics Tracking

This plan outlines how to.

## Architecture & Design

### 1. Global Rule Configuration (`.agents/rules/prompt_heuristics.md`)
- **Location**: `.agents/rules/prompt_heuristics.md`
- **Trigger**: `trigger: always_on`
- **Behavior**: The LLM natively evaluates every incoming user prompt against the 9 prompt.

### 2. Generic Post-Invocation SQLite Logging Hook (`.agents/hooks/log_rule_trigger.py`)
- **Script**: `.agents/hooks/log_rule_trigger.py`
- **Trigger**: Registered in `.agents/hooks.json` under `PostInvocation`.
- **Database**: `.agents/metrics.db` (SQLite).
- **Schema**:
```sql
CREATE TABLE IF NOT EXISTS rule_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    prompt_snippet TEXT
);
```

### 3. SQLite Metrics Aggregator & Installer
- **Script**: `.agents/scripts/prompt_metrics.py` (queries `.agents/metrics.db`).
- **Installer**: `install.sh` (deploys `.agents/rules/prompt_heuristics.md` to `~/.gemini/config/rules/`).

---

## Steps to Execute (When Ready):

1. Move `.agents/prompt_heuristics.md` to `.agents/rules/prompt_heuristics.md`.
2. Add `[RULE_TRIGGER: <Rule Name>]` logging instruction to `.agents/rules/prompt_heuristics.md`.
3. Create `.agents/hooks/log_rule_trigger.py` using Python's.
4. Update `.agents/hooks.json` to use `PostInvocation` for `log_rule_trigger.py` (removing the pre-screening hook).
5. Update `.agents/scripts/prompt_metrics.py` to query `.agents/metrics.db`.
6. Update `install.sh` and run `./install.sh --global`.
