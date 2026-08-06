"""Unit test verifying agent system instruction rules and initial engagement flow for BUG-015."""

import pytest
from app.cch_agent.agent import CCH_SYSTEM_INSTRUCTION


def test_initial_engagement_no_premature_document_demand():
    """Verify system instruction does not demand discharge documents immediately upon initial identity confirmation (BUG-015 / BUG-006)."""
    assert "Do NOT demand or ask for discharge documents immediately" in CCH_SYSTEM_INSTRUCTION
    assert "Wait for the parent to state their question or intent first" in CCH_SYSTEM_INSTRUCTION


def test_demo_safety_guardrails():
    """Verify system instruction contains NSFW / safety refusal guardrails (BUG-010)."""
    assert "Strict Scope Control & Demo Safety Guardrails" in CCH_SYSTEM_INSTRUCTION
    assert "refuse any inappropriate, offensive, sexually explicit, or NSFW user inputs" in CCH_SYSTEM_INSTRUCTION


def test_multi_page_detection_guardrail():
    """Verify system instruction contains strict multi-page vision guardrail (BUG-009)."""
    assert "Strict Multi-Page Detection" in CCH_SYSTEM_INSTRUCTION
    assert "Do NOT invent, hallucinate, or claim multi-page indicators on single-page documents" in CCH_SYSTEM_INSTRUCTION


def test_date_awareness_guardrail():
    """Verify system instruction contains dynamic Date Awareness constraint (BUG-19)."""
    assert "Date Awareness" in CCH_SYSTEM_INSTRUCTION
    assert "Today's actual current date is" in CCH_SYSTEM_INSTRUCTION


def test_exact_practitioner_mapping_guardrail():
    """Verify system instruction contains exact practitioner mapping rule (BUG-29)."""
    assert "Exact Practitioner Mapping" in CCH_SYSTEM_INSTRUCTION
    assert "MUST accurately map their selection to the exact practitioner name" in CCH_SYSTEM_INSTRUCTION


def test_turn_pacing_guardrail():
    """Verify system instruction contains conversational turn pacing and question waiting constraint (BUG-33)."""
    assert "Conversational Turn Pacing & Waiting for User Response" in CCH_SYSTEM_INSTRUCTION
    assert "ALWAYS wait for the parent to answer before proceeding" in CCH_SYSTEM_INSTRUCTION

