import unittest
import json
import urllib.parse
import server

class DummyHandler:
    def __init__(self):
        self.sent_data = None
        self.sent_code = None
        self.headers = {}
    def send_json(self, data, status_code=200):
        self.sent_data = data
        self.sent_code = status_code

class TestServerRationalizedAPI(unittest.TestCase):

    def test_status_endpoint(self):
        """Verify GET /api/status returns unified health and snapshot state."""
        handler = DummyHandler()
        server.DashboardHandler.handle_status(handler, "project=sample")
        self.assertEqual(handler.sent_code, 200)
        self.assertIsNotNone(handler.sent_data)
        self.assertEqual(handler.sent_data.get('project'), 'sample')
        self.assertIn('total_snapshots', handler.sent_data)
        self.assertIn('total_risks', handler.sent_data)

    def test_sync_endpoint(self):
        """Verify POST /api/sync executes unified synchronization."""
        handler = DummyHandler()
        server.DashboardHandler.handle_sync(handler, {'project': 'sample'})
        self.assertEqual(handler.sent_code, 200)
        self.assertIsNotNone(handler.sent_data)
        self.assertEqual(handler.sent_data.get('status'), 'ok')
        self.assertEqual(handler.sent_data.get('project'), 'sample')

    def test_ingest_endpoint(self):
        """Verify POST /api/ingest parses report and persists snapshot."""
        handler = DummyHandler()
        params = {
            'project': 'sample',
            'fileName': 'Weekly Reporting - Week 28 - 14 Aug 2026.pdf',
            'fileId': 'mock-w28-id',
            'fallback': True
        }
        server.DashboardHandler.handle_ingest(handler, params)
        self.assertEqual(handler.sent_code, 200)
        self.assertIsNotNone(handler.sent_data)
        self.assertEqual(handler.sent_data.get('status'), 'ok')
        self.assertIn('Week 28', handler.sent_data.get('message', ''))

    def test_briefing_generate_endpoint(self):
        """Verify POST /api/briefing/generate regenerates synthesis and podcast."""
        handler = DummyHandler()
        params = {
            'project': 'sample',
            'week': 'Week 28',
            'fallback': True
        }
        server.DashboardHandler.handle_briefing(handler, params)
        self.assertEqual(handler.sent_code, 200)
        self.assertIsNotNone(handler.sent_data)
        self.assertEqual(handler.sent_data.get('status'), 'ok')
        self.assertIn('synthesis', handler.sent_data)

    def test_legacy_aliases_backward_compatible(self):
        """Verify legacy endpoints like /api/sync-sheet still function via routing aliases."""
        handler = DummyHandler()
        server.DashboardHandler.handle_sync_sheet(handler, "project=sample")
        self.assertEqual(handler.sent_code, 200)
        self.assertIsNotNone(handler.sent_data)
        self.assertIn('snapshots', handler.sent_data)
