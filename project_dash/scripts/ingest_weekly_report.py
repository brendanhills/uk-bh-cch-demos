import os
import sys
import json
import argparse
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.gemini_generator import generate_executive_synthesis, generate_multispeaker_podcast, get_gemini_client

logger = logging.getLogger('ingest_weekly_report')

def get_project_dir(project_name: str = 'sample') -> str:
    """Resolves the data directory for a given project."""
    proj_dir = os.path.join(BASE_DIR, 'data', project_name)
    if os.path.exists(proj_dir):
        return proj_dir
    # Fallback to src/data if migrating
    legacy_dir = os.path.join(BASE_DIR, 'src', 'data')
    if os.path.exists(legacy_dir):
        return legacy_dir
    os.makedirs(proj_dir, exist_ok=True)
    return proj_dir

def load_json_file(file_path: str, default: Any = None) -> Any:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
    return default if default is not None else {}

def save_json_file(file_path: str, data: Any):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def compute_risk_metrics(risks: list, issues: list) -> dict:
    total_risks = len(risks)
    total_issues = len(issues)
    
    if not risks:
        return {
            'total_risks': 0,
            'inherent_avg_score': 0.0,
            'residual_avg_score': 0.0,
            'delta_compression': '0.0',
            'eventuated_issues_count': 0,
            'total_issues': total_issues
        }

    inh_scores = [float(r.get('inherentRiskScore', 1) or 1) for r in risks]
    res_scores = [float(r.get('residualRiskScore', 1) or 1) for r in risks]
    
    inh_avg = round(sum(inh_scores) / len(inh_scores), 1) if inh_scores else 0.0
    res_avg = round(sum(res_scores) / len(res_scores), 1) if res_scores else 0.0
    delta = round(res_avg - inh_avg, 1)

    eventuated = len([r for r in risks if 'eventuated' in str(r.get('status', '')).lower()])

    return {
        'total_risks': total_risks,
        'inherent_avg_score': inh_avg,
        'residual_avg_score': res_avg,
        'delta_compression': f"{delta:+.1f}" if delta != 0 else "0.0",
        'eventuated_issues_count': eventuated,
        'total_issues': total_issues
    }

def ingest_file(
    file_id: str,
    file_name: str,
    week_number: int = None,
    report_date: str = None,
    project_name: str = None,
    generate_ai: bool = False,
    model: str = 'gemini-3.5-flash'
):
    # Handle backward compatibility if project_name passed in positional args
    if isinstance(week_number, str) and not str(week_number).isdigit():
        project_name = week_number
        week_number = None

    project_name = project_name or os.getenv('ACTIVE_PROJECT', 'sample')
    proj_dir = get_project_dir(project_name)
    snapshots_file = os.path.join(proj_dir, 'snapshots.json')
    if not os.path.exists(snapshots_file):
        # Check legacy path
        legacy_snap = os.path.join(BASE_DIR, 'src', 'data', 'weekly_snapshots.json')
        if os.path.exists(legacy_snap):
            snapshots_file = legacy_snap

    risks_file = os.path.join(proj_dir, 'risks.json')
    if not os.path.exists(risks_file):
        risks_file = os.path.join(BASE_DIR, 'src', 'data', 'live_synced_data.json')

    issues_file = os.path.join(proj_dir, 'issues.json')
    knowledge_file = os.path.join(proj_dir, 'knowledge.json')

    snapshots_data = load_json_file(snapshots_file, {'snapshots': {}})
    risks_raw = load_json_file(risks_file, [])
    risks = risks_raw.get('risks', risks_raw) if isinstance(risks_raw, dict) else risks_raw
    issues_raw = load_json_file(issues_file, [])
    issues = issues_raw.get('issues', issues_raw) if isinstance(issues_raw, dict) else issues_raw
    knowledge = load_json_file(knowledge_file, {'blueprints': []})

    # Determine week number and date
    if not week_number:
        m = re.search(r'Week\s*(\d+)', file_name, re.IGNORECASE)
        existing_weeks = [s.get('weekNumber', 0) for s in snapshots_data.get('snapshots', {}).values()]
        week_number = int(m.group(1)) if m else (max(existing_weeks or [26]) + 1)

    if not report_date:
        m = re.search(r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})', file_name)
        report_date = m.group(1) if m else datetime.now().strftime("%d %b %Y")

    week_key = f"w{week_number}"
    week_label = f"Week {week_number}"
    print(f"Ingesting {file_name} as {week_label} ({report_date}) for project '{project_name}'...")

    # Locate previous baseline week
    sorted_prior = sorted([s for s in snapshots_data.get('snapshots', {}).values() if s.get('weekNumber', 0) < week_number], key=lambda x: x.get('weekNumber', 0))
    prior_snap = sorted_prior[-1] if sorted_prior else {}
    baseline_week = prior_snap.get('weekLabel', f"Week {max(1, week_number - 1)}")
    baseline_date = prior_snap.get('date', 'Previous Cycle')

    # Default plans
    raw_plans = prior_snap.get('plans', [])
    if raw_plans and len(raw_plans) >= 4:
        plans = raw_plans
    else:
        plans = [
            {'num': 1, 'status': 'RED', 'ref': '1.2b', 'title': 'Milestone 1 Deliverables Acceptance', 'plan': 'Work with customer for sign-off.', 'owner': 'Delivery Lead', 'target': 'Aug 2026'},
            {'num': 2, 'status': 'RED', 'ref': '1.6 GFF', 'title': 'Facilities & Connectivity', 'plan': 'Mitigate lead time.', 'owner': 'Infrastructure Lead', 'target': 'Aug 2026'},
            {'num': 3, 'status': 'BLUE', 'ref': '1.10b', 'title': 'Platform E.01 Ready', 'plan': 'Operational for test/dev.', 'owner': 'Engineering Lead', 'target': 'Delivered'},
            {'num': 4, 'status': 'RED', 'ref': '1.14', 'title': 'Systems Requirements Review (SRR)', 'plan': 'Iterative requirements alignment.', 'owner': 'Technical Lead', 'target': 'Sep 2026'}
        ]

    risk_metrics = compute_risk_metrics(risks, issues)
    metric_ctx = {
        'report_week': week_label,
        'report_date': report_date,
        'baseline_week': baseline_week,
        'baseline_date': baseline_date,
        'overall_status': '🟡 AMBER (Stable)',
        'commercial_status': '🟢 ON TRACK',
        'ibr_status': '🟡 DUE AUG 2026 (90%)',
        'ato_status': '🟢 GREEN',
        'escalations_count': 5,
        **risk_metrics
    }

    synthesis_result = {}
    podcast_script = []

    if generate_ai:
        try:
            print(f"Calling Gemini API ({model}) for structured executive briefing synthesis...")
            synthesis_result = generate_executive_synthesis(metric_ctx, plans, model=model)
            podcast_script = generate_multispeaker_podcast(metric_ctx, synthesis_result, model=model)
            print("Gemini synthesis & podcast script successfully generated.")
        except Exception as e:
            print(f"Warning: AI Generation encountered an error: {e}")
            synthesis_result = {
                'synthesis': {
                    'executive': f"Program posture for {week_label} maintains a stable AMBER status with active mitigation across {risk_metrics['total_risks']} registered risks. Net risk compression reduced exposure from {risk_metrics['inherent_avg_score']} to {risk_metrics['residual_avg_score']}.",
                    'technical': f"Technical velocity confirms key milestones on track with ongoing security accreditation and environment validation.",
                    'governance': f"Governance alignment continues across key deliverable gates with {risk_metrics['total_issues']} active blockers under remediation."
                },
                'top3': [
                    {'num': 1, 'type': 'decision', 'tag': '🚨 Immediate Action', 'ref': '1.2b', 'title': 'Milestone Sign-Off', 'action': 'Expedite acceptance review.'},
                    {'num': 2, 'type': 'schedule', 'tag': '⚡ Schedule Alignment', 'ref': '1.14', 'title': 'SRR Glide Path', 'action': 'Align September requirements baseline.'},
                    {'num': 3, 'type': 'win', 'tag': '🚀 Delivery Win', 'ref': '1.10b', 'title': 'Platform Ready', 'action': 'Early test/dev onboarding operational.'}
                ],
                'sleeperOutlier': {
                    'ref': '1.15',
                    'title': 'Milestone 3 PDR',
                    'warning': 'Schedule compression created by upstream SRR glide path.'
                },
                'generatedBy': 'rule-based-baseline'
            }
            podcast_script = [
                {'speaker': 'Alex', 'role': 'Program Analyst', 'avatar': '🎙️', 'time': '0:00', 'text': f"Welcome to the Executive Briefing for {week_label}, ending {report_date}."},
                {'speaker': 'Jordan', 'role': 'Technical Director', 'avatar': '🤖', 'time': '0:18', 'text': f"Our net risk exposure improved to {risk_metrics['residual_avg_score']} this week with core platform milestones on track."}
            ]

    # Mark previous as not latest
    for k, v in snapshots_data.get('snapshots', {}).items():
        v['isLatest'] = False
        v['isCurrent'] = False

    new_snapshot = {
        'weekNumber': week_number,
        'weekLabel': week_label,
        'week': week_label,
        'date': report_date,
        'isLatest': True,
        'isCurrent': True,
        'driveFileId': file_id,
        'driveFileName': file_name,
        'overallStatus': metric_ctx['overall_status'],
        'kpis': {
            'commercial': metric_ctx['commercial_status'],
            'ibr': metric_ctx['ibr_status'],
            'ato': metric_ctx['ato_status'],
            'escalations': f"🔴 {metric_ctx['escalations_count']} ITEMS"
        },
        'synthesis': synthesis_result.get('synthesis', {}),
        'top3': synthesis_result.get('top3', []),
        'sleeperOutlier': synthesis_result.get('sleeperOutlier', {}),
        'podcastScript': podcast_script,
        'plans': plans,
        'generatedBy': synthesis_result.get('generatedBy', model)
    }

    snapshots_data['snapshots'][week_key] = new_snapshot
    snapshots_data['lastSynced'] = datetime.now().isoformat()
    save_json_file(snapshots_file, snapshots_data)
    print(f"Saved snapshot to {snapshots_file}")

    return new_snapshot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest weekly reporting pack with Gemini AI synthesis')
    parser.add_argument('--project', default=os.getenv('ACTIVE_PROJECT', 'sample'), help='Target project slug')
    parser.add_argument('--file-id', default='dummy-id-w28', help='Google Drive file ID')
    parser.add_argument('--name', default='Weekly Reporting - Week 28 - 14 Aug 2026.pdf', help='Report file name')
    parser.add_argument('--week', type=int, help='Week number')
    parser.add_argument('--date', help='Report date')
    parser.add_argument('--model', default='gemini-3.5-flash', help='Gemini model to use')
    parser.add_argument('--no-ai', dest='generate_ai', action='store_false', help='Skip Gemini AI generation')
    args = parser.parse_args()

    ingest_file(
        file_id=args.file_id,
        file_name=args.name,
        project_name=args.project,
        week_number=args.week,
        report_date=args.date,
        generate_ai=args.generate_ai,
        model=args.model
    )
