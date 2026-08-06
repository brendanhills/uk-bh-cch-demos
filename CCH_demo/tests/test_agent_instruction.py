"""Unit tests verifying agent router and sub-agent instructions."""

import pytest
from app.cch_agent.agent import ROUTER_INSTRUCTION
from app.cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)


def test_router_instruction():
    """Verify master concierge router instruction defines delegation roles."""
    assert "Master Concierge Router Agent" in ROUTER_INSTRUCTION
    assert "patient_verifier" in ROUTER_INSTRUCTION
    assert "document_scanner" in ROUTER_INSTRUCTION
    assert "visit_scheduler" in ROUTER_INSTRUCTION
    assert "soap_generator" in ROUTER_INSTRUCTION


def test_patient_verifier_instruction():
    """Verify patient_verifier sub-agent handles greeting and identity confirmation."""
    assert "Patient Verification Specialist" in patient_verifier.instruction
    assert "confirm who you are speaking with" in patient_verifier.instruction


def test_document_scanner_multi_page_guardrail():
    """Verify document_scanner sub-agent contains multi-page vision guardrail (#BUG-009)."""
    assert "Multi-Page Detection Guardrail" in document_scanner.instruction
    assert "Do NOT claim multi-page indicators on single-page documents" in document_scanner.instruction


def test_visit_scheduler_practitioner_mapping():
    """Verify visit_scheduler sub-agent contains exact practitioner mapping rule (#BUG-29)."""
    assert "Exact Practitioner Mapping" in visit_scheduler.instruction
    assert "accurately map their choice to the exact practitioner name" in visit_scheduler.instruction
