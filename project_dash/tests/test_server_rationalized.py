"""Unit tests for the rationalized REST API endpoints in server.py."""

import json
import pytest

import server
from tests.conftest import DummyHandler


def test_status_endpoint(dummy_handler: DummyHandler):
    """Verify GET /api/status returns unified health and snapshot state."""
    server.DashboardHandler.handle_status(dummy_handler, "project=sample")
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert dummy_handler.sent_data.get('project') == 'sample'
    assert 'total_snapshots' in dummy_handler.sent_data
    assert 'total_risks' in dummy_handler.sent_data


def test_sync_endpoint(dummy_handler: DummyHandler):
    """Verify POST /api/sync executes unified synchronization."""
    server.DashboardHandler.handle_sync(dummy_handler, {'project': 'sample'})
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert dummy_handler.sent_data.get('status') == 'ok'
    assert dummy_handler.sent_data.get('project') == 'sample'


def test_ingest_endpoint(dummy_handler: DummyHandler):
    """Verify POST /api/ingest parses report and persists snapshot."""
    params = {
        'project': 'sample',
        'fileName': 'Weekly Reporting - Week 28 - 14 Aug 2026.pdf',
        'fileId': 'mock-w28-id',
        'fallback': True
    }
    server.DashboardHandler.handle_ingest(dummy_handler, params)
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert dummy_handler.sent_data.get('status') == 'ok'
    assert 'Week 28' in dummy_handler.sent_data.get('message', '')


def test_briefing_generate_endpoint(dummy_handler: DummyHandler):
    """Verify POST /api/briefing/generate regenerates synthesis and podcast."""
    params = {
        'project': 'sample',
        'week': 'Week 28',
        'fallback': True
    }
    server.DashboardHandler.handle_briefing(dummy_handler, params)
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert dummy_handler.sent_data.get('status') == 'ok'
    assert 'synthesis' in dummy_handler.sent_data


def test_legacy_aliases_backward_compatible(dummy_handler: DummyHandler):
    """Verify legacy endpoints like /api/sync-sheet still function via routing aliases."""
    server.DashboardHandler.handle_sync_sheet(dummy_handler, "project=sample")
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert 'snapshots' in dummy_handler.sent_data
