import os
import sys
import json
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.pipeline import (
    parse_report_metadata,
    compute_risk_metrics,
    generate_fallback_synthesis,
    generate_fallback_podcast,
    sync_project_data,
    ingest_report_file
)
import scripts.gemini_generator as gg

class TestPipeline(unittest.TestCase):

    def test_parse_report_metadata_various_formats(self):
        # Standard format
        meta1 = parse_report_metadata("Weekly Reporting - Week 28 - 14 Aug 2026.pdf", use_gemini=False)
        self.assertEqual(meta1['week_number'], 28)
        self.assertEqual(meta1['report_date'], "14 Aug 2026")
        self.assertEqual(meta1['week_label'], "Week 28")

        # W29 abbreviation format
        meta2 = parse_report_metadata("W29_Executive_Summary_21Aug2026.pdf", use_gemini=False)
        self.assertEqual(meta2['week_number'], 29)
        self.assertIn("Aug", meta2['report_date'])

        # Non-standard name with fallback
        meta3 = parse_report_metadata("Status_Report_Final.pdf", fallback_week=30, use_gemini=False)
        self.assertEqual(meta3['week_number'], 30)
        self.assertEqual(meta3['week_label'], "Week 30")

    def test_compute_risk_metrics(self):
        risks = [
            {"inherentRiskScore": 20, "residualRiskScore": 6, "status": "Active"},
            {"inherentRiskScore": 15, "residualRiskScore": 9, "status": "Eventuated"},
            {"inherentRiskScore": 10, "residualRiskScore": 4, "status": "Active"}
        ]
        issues = [{"id": "ISS-01"}, {"id": "ISS-02"}]
        metrics = compute_risk_metrics(risks, issues)

        self.assertEqual(metrics['total_risks'], 3)
        self.assertEqual(metrics['total_issues'], 2)
        self.assertEqual(metrics['eventuated_issues_count'], 1)
        self.assertEqual(metrics['inherent_avg_score'], 15.0)
        self.assertEqual(metrics['residual_avg_score'], 6.3)
        self.assertEqual(metrics['delta_compression'], "-8.7")

    def test_generate_fallback_synthesis(self):
        metrics = {
            'report_week': 'Week 28',
            'report_date': '14 Aug 2026',
            'total_risks': 14,
            'inherent_avg_score': 15.4,
            'residual_avg_score': 6.2,
            'delta_compression': '-9.2',
            'total_issues': 5,
            'eventuated_issues_count': 1
        }
        synthesis = generate_fallback_synthesis(metrics)
        self.assertIn('synthesis', synthesis)
        self.assertIn('top3', synthesis)
        self.assertIn('sleeperOutlier', synthesis)
        self.assertEqual(len(synthesis['top3']), 3)
        self.assertIn('executive', synthesis['synthesis'])
        self.assertEqual(synthesis['generatedBy'], 'deterministic_rule_engine')

    def test_generate_fallback_podcast(self):
        metrics = {'report_week': 'Week 28', 'report_date': '14 Aug 2026'}
        synthesis = generate_fallback_synthesis(metrics)
        podcast = generate_fallback_podcast(metrics, synthesis)
        self.assertIsInstance(podcast, list)
        self.assertGreaterEqual(len(podcast), 4)
        self.assertEqual(podcast[0]['speaker'], 'Alex')
        self.assertEqual(podcast[1]['speaker'], 'Jordan')

    def test_ingest_report_file_sandbox(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_dir = os.path.join(tmp_dir, 'sample')
            os.makedirs(proj_dir, exist_ok=True)
            
            # Create baseline risks.json
            risks_path = os.path.join(proj_dir, 'risks.json')
            with open(risks_path, 'w') as f:
                json.dump([{"inherentRiskScore": 16, "residualRiskScore": 8, "status": "Active"}], f)

            # Ingest a new report
            result = ingest_report_file(
                file_name="Weekly Reporting - Week 29 - 21 Aug 2026.pdf",
                project_name="sample",
                data_root=tmp_dir,
                force_fallback=True
            )

            self.assertTrue(result['success'])
            self.assertEqual(result['week'], 29)

            # Check snapshots.json was created/updated
            snap_path = os.path.join(proj_dir, 'snapshots.json')
            self.assertTrue(os.path.exists(snap_path))
            with open(snap_path, 'r') as f:
                snaps = json.load(f)
            self.assertIn('Week 29', snaps)
            self.assertEqual(snaps['Week 29']['metrics']['total_risks'], 1)

    @patch('scripts.gemini_generator.inspect_report_with_gemini')
    def test_parse_report_metadata_gemini_multimodal(self, mock_inspect):
        mock_inspect.return_value = {
            'week_number': 31,
            'week_label': 'Week 31',
            'report_date': '28 Aug 2026',
            'title': 'Monaro Executive Risk Review',
            'summary': 'Week 31 summary pack',
            'inspectedBy': 'gemini-3.5-flash'
        }

        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            meta = parse_report_metadata(tmp_file.name, use_gemini=True)
            self.assertEqual(meta['week_number'], 31)
            self.assertEqual(meta['week_label'], 'Week 31')
            self.assertEqual(meta['report_date'], '28 Aug 2026')
            self.assertEqual(meta['inspectedBy'], 'gemini-3.5-flash')
            mock_inspect.assert_called_once()

    @patch('scripts.gemini_generator.inspect_report_with_gemini')
    def test_parse_report_metadata_gemini_fallback_on_error(self, mock_inspect):
        mock_inspect.side_effect = RuntimeError("API quota exceeded")

        meta = parse_report_metadata("Weekly Reporting - Week 28 - 14 Aug 2026.pdf", use_gemini=True)
        self.assertEqual(meta['week_number'], 28)
        self.assertEqual(meta['report_date'], "14 Aug 2026")
        self.assertEqual(meta['inspectedBy'], 'regex_heuristic')

if __name__ == '__main__':
    unittest.main()


