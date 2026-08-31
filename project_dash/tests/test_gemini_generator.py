"""Unit tests for Gemini generator and multimodal executive briefing synthesis."""

import json
from unittest.mock import patch, MagicMock
import pytest

from scripts.gemini_generator import (
    get_gemini_client,
    generate_executive_synthesis,
    generate_multispeaker_podcast,
    build_synthesis_prompt,
    ExecutiveSynthesisResult,
    PodcastDialogueTurn
)


def test_client_init_adc_priority(monkeypatch: pytest.MonkeyPatch):
    """Verify Gemini client prioritizes Vertex AI ADC configuration when project and region are set."""
    monkeypatch.setenv('GCP_PROJECT_ID', 'test-project')
    monkeypatch.setenv('GCP_REGION', 'us-central1')
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')

    with patch('google.genai.Client') as mock_client:
        client = get_gemini_client()
        mock_client.assert_called_with(vertexai=True, project='test-project', location='us-central1')


def test_client_init_api_key_fallback(monkeypatch: pytest.MonkeyPatch):
    """Verify Gemini client falls back to API key when Vertex AI environment variables are absent."""
    monkeypatch.delenv('GCP_PROJECT_ID', raising=False)
    monkeypatch.setenv('GEMINI_API_KEY', 'valid-api-key')

    with patch('google.genai.Client') as mock_client:
        client = get_gemini_client()
        mock_client.assert_called_with(api_key='valid-api-key')


def test_build_synthesis_prompt():
    """Verify prompt formatting with metrics, reporting dates, and milestone plans."""
    metrics = {
        'report_week': 'Week 28',
        'report_date': '14 Aug 2026',
        'baseline_week': 'Week 27',
        'baseline_date': '07 Aug 2026',
        'overall_status': '🟡 AMBER (Stable)',
        'commercial_status': '🟢 ON TRACK',
        'ibr_status': '🟡 DUE AUG 2026 (90%)',
        'ato_status': '🟢 GREEN',
        'escalations_count': 5,
        'total_risks': 107,
        'inherent_avg_score': 15.4,
        'residual_avg_score': 8.4,
        'delta_compression': '-7.0',
        'eventuated_issues_count': 21,
        'total_issues': 29
    }
    plans = [
        {'num': 1, 'ref': '1.2b', 'title': 'Milestone 1 Acceptance', 'plan': 'Accelerate Cth reviews.', 'owner': 'Adam Flint', 'target': 'Aug 2026'}
    ]
    prompt = build_synthesis_prompt(metrics, plans)
    assert 'Week 28' in prompt
    assert '14 Aug 2026' in prompt
    assert '15.4' in prompt
    assert 'Milestone 1 Acceptance' in prompt


def test_parse_structured_synthesis_json():
    """Verify structured response parsing of executive synthesis, top 3 items, and sleeper outlier."""
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        'synthesis': {
            'executive': 'Executive summary paragraph test.',
            'technical': 'Technical summary paragraph test.',
            'governance': 'Governance summary paragraph test.'
        },
        'top3': [
            {
                'num': 1,
                'type': 'decision',
                'tag': '🚨 Immediate Action',
                'ref': '1.2b',
                'title': 'Cth Acceptance',
                'action': 'Expedite sign-off.'
            }
        ],
        'sleeperOutlier': {
            'ref': '1.15',
            'title': 'Milestone 3 PDR',
            'warning': 'Schedule squeeze due to SRR alignment.'
        }
    })

    with patch('scripts.gemini_generator.get_gemini_client') as mock_get_client:
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client_instance

        result = generate_executive_synthesis({}, [], model='gemini-3.5-flash')
        assert result['synthesis']['executive'] == 'Executive summary paragraph test.'
        assert len(result['top3']) == 1
        assert result['sleeperOutlier']['ref'] == '1.15'
