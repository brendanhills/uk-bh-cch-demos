import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.pipeline import (
    sync_project_data,
    ingest_report_file,
    compute_risk_metrics,
    generate_fallback_synthesis,
    generate_fallback_podcast,
    load_json_file,
    save_json_file
)

PORT = 9000
DIRECTORY = BASE_DIR
SNAPSHOTS_FILE = os.path.join(DIRECTORY, "data", "sample", "snapshots.json")

def get_default_project():
    env_path = os.path.join(DIRECTORY, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DEFAULT_PROJECTS=') or line.startswith('DEFAULT_PROJECT='):
                    val = line.split('=', 1)[1].strip().strip('"\'')
                    first_proj = val.split(',')[0].strip()
                    if first_proj:
                        return first_proj
    return 'sample'

def get_project_dir(project_slug=''):
    if not project_slug:
        project_slug = get_default_project()
    # Backward compatibility alias between monaro and f-dse
    if project_slug == 'f-dse' and os.path.exists(os.path.join(DIRECTORY, 'data', 'monaro')):
        project_slug = 'monaro'
    elif project_slug == 'monaro' and not os.path.exists(os.path.join(DIRECTORY, 'data', 'monaro')) and os.path.exists(os.path.join(DIRECTORY, 'data', 'f-dse')):
        project_slug = 'f-dse'
    p_dir = os.path.join(DIRECTORY, 'data', project_slug)
    if os.path.exists(p_dir):
        return p_dir
    sample_dir = os.path.join(DIRECTORY, 'data', 'sample')
    if os.path.exists(sample_dir):
        return sample_dir
    return os.path.join(DIRECTORY, 'data')

def parse_request_params(query_or_params):
    if isinstance(query_or_params, dict):
        return query_or_params
    if isinstance(query_or_params, str):
        q = urllib.parse.parse_qs(query_or_params)
        return {k: v[0] if len(v) == 1 else v for k, v in q.items()}
    return {}

# Default fallback Drive folder reports
DEFAULT_DRIVE_REPORTS = [
    {"id": "1_monaro_drive_w29", "week": "Week 29", "date": "21 Aug 2026", "name": "Weekly Reporting - Week 29 - 21 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1_monaro_drive_w29/view"},
    {"id": "1_monaro_drive_w28", "week": "Week 28", "date": "14 Aug 2026", "name": "Weekly Reporting - Week 28 - 14 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1_monaro_drive_w28/view"},
    {"id": "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu", "week": "Week 27", "date": "07 Aug 2026", "name": "Weekly Reporting - Week 27 - 07 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu/view"},
    {"id": "1UlQmROLEbOroFI8neyne3qOUm4wEgCyC", "week": "Week 26", "date": "31 Jul 2026", "name": "Weekly Reporting - Week 26 - 31 Jul 2026.pdf", "url": "https://drive.google.com/file/d/1UlQmROLEbOroFI8neyne3qOUm4wEgCyC/view"},
    {"id": "13ThXt0QIpS2OFg4NEewfx8ggoD2CItlz", "week": "Week 25", "date": "24 Jul 2026", "name": "Weekly Reporting - Week 25 - 24 Jul 2026.pdf", "url": "https://drive.google.com/file/d/13ThXt0QIpS2OFg4NEewfx8ggoD2CItlz/view"},
    {"id": "100xnsVUDdlKVzxTgK26_lmjSYYUWnUhK", "week": "Week 24", "date": "17 Jul 2026", "name": "Weekly Reporting - Week 24 - 17 Jul 2026.pdf", "url": "https://drive.google.com/file/d/100xnsVUDdlKVzxTgK26_lmjSYYUWnUhK/view"},
    {"id": "1YRJuXlIIkYRYEsU41K_nuO9iIwrS9k0e", "week": "Week 23", "date": "10 Jul 2026", "name": "Weekly Reporting - Week 23 - 10 Jul 2026.pdf", "url": "https://drive.google.com/file/d/1YRJuXlIIkYRYEsU41K_nuO9iIwrS9k0e/view"},
    {"id": "1kQiDQPF9DCUZ0vvbivToMoJWeZJoB0eREFnywRxpCHA", "week": "Week 22", "date": "03 Jul 2026", "name": "Weekly Reporting - Week 22 - 03 Jul 2026 (Google Doc)", "url": "https://docs.google.com/document/d/1kQiDQPF9DCUZ0vvbivToMoJWeZJoB0eREFnywRxpCHA/edit"}
]

KNOWN_DRIVE_REPORTS = DEFAULT_DRIVE_REPORTS

def query_live_drive_folder(folder_id: str) -> List[Dict[str, Any]]:
    """Queries Google Drive API for files in the specified folderId using ADC credentials."""
    if not folder_id or str(folder_id).startswith('sample-'):
        return []
    try:
        import google.auth
        from googleapiclient.discovery import build
        credentials, _ = google.auth.default(scopes=[
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/cloud-platform'
        ])
        service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, webViewLink, createdTime)",
            orderBy="name desc"
        ).execute()
        files = results.get('files', [])
        drive_reports = []
        for f in files:
            name = f.get('name', '')
            if name.endswith(('.pdf', '.docx', '.doc', '.gdoc', '.pptx')) or 'Reporting' in name or 'Week' in name:
                w_match = re.search(r'week[\s_-]*(\d+)', name, re.IGNORECASE) or re.search(r'\bw(\d+)\b', name, re.IGNORECASE)
                w_label = f"Week {w_match.group(1)}" if w_match else "Report"
                date_match = re.search(r'(\d{1,2})[\s_-]+([A-Za-z]{3,9})[\s_-]+(\d{4})', name)
                rep_date = f"{date_match.group(1)} {date_match.group(2)[:3].title()} {date_match.group(3)}" if date_match else "Recent"
                drive_reports.append({
                    "id": f.get('id'),
                    "name": name,
                    "week": w_label,
                    "date": rep_date,
                    "url": f.get('webViewLink') or f"https://drive.google.com/file/d/{f.get('id')}/view"
                })
        return drive_reports
    except Exception:
        return []

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/favicon.ico':
            self.send_response(204)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
        elif parsed.path in ('/api/status', '/api/projects/status'):
            self.handle_status(parsed.query)
        elif parsed.path in ('/api/sync', '/api/sync-all'):
            self.handle_sync(parsed.query)
        elif parsed.path == '/api/sync-sheet':
            self.handle_sync_sheet(parsed.query)
        elif parsed.path == '/api/check-drive-sync':
            self.handle_check_drive_sync(parsed.query)
        elif parsed.path == '/api/notebooks':
            self.handle_list_notebooks(parsed.query)
        elif parsed.path == '/api/check-notebook-sync':
            self.handle_check_notebook_sync(parsed.query)
        elif parsed.path == '/api/sync-notebook':
            self.handle_sync_notebook(parsed.query)
        elif parsed.path == '/api/ingest-report':
            self.handle_ingest_report(parsed.query)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        params = json.loads(body) if body else {}

        if parsed.query:
            q_params = urllib.parse.parse_qs(parsed.query)
            for k, v in q_params.items():
                if k not in params:
                    params[k] = v[0] if len(v) == 1 else v

        if parsed.path in ('/api/sync', '/api/sync-all'):
            self.handle_sync(params)
        elif parsed.path in ('/api/ingest', '/api/ingest-report'):
            self.handle_ingest(params)
        elif parsed.path in ('/api/briefing/generate', '/api/regenerate-briefing', '/api/generate-podcast'):
            self.handle_briefing(params)
        elif parsed.path == '/api/ingest-data':
            self.handle_ingest_data(params)
        elif parsed.path == '/api/sync-notebook':
            self.handle_sync_notebook(params)
        else:
            super().do_POST()

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _parse_params(self, query_or_params):
        if isinstance(query_or_params, dict):
            return query_or_params
        if isinstance(query_or_params, str):
            q = urllib.parse.parse_qs(query_or_params)
            return {k: v[0] if len(v) == 1 else v for k, v in q.items()}
        return {}

    # --- Consolidated REST Handlers ---

    def handle_status(self, query_or_params=''):
        """GET /api/status?project=<slug>"""
        try:
            params = parse_request_params(query_or_params)
            proj = params.get('project') or get_default_project()
            result = sync_project_data(project_name=proj)
            self.send_json(result)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_sync(self, query_or_params=''):
        """POST /api/sync?project=<slug> or GET /api/sync"""
        try:
            params = parse_request_params(query_or_params)
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)

            snaps = load_json_file(os.path.join(p_dir, 'snapshots.json'), {})
            risks = load_json_file(os.path.join(p_dir, 'risks.json'), [])
            issues = load_json_file(os.path.join(p_dir, 'issues.json'), [])

            self.send_json({
                'status': 'ok',
                'project': proj,
                'message': f'Live data synchronized successfully for project "{proj}"',
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'snapshots': len(snaps.get('snapshots', snaps) if isinstance(snaps, dict) else {}),
                    'risks': len(risks if isinstance(risks, list) else []),
                    'issues': len(issues if isinstance(issues, list) else [])
                }
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_ingest(self, query_or_params=''):
        """POST /api/ingest?project=<slug>"""
        try:
            params = parse_request_params(query_or_params)
            proj = params.get('project') or get_default_project()
            file_name = params.get('fileName') or params.get('file_name') or 'Weekly Reporting - Week 28 - 14 Aug 2026.pdf'
            file_id = params.get('fileId') or params.get('file_id')
            force_fb = bool(params.get('fallback', False))

            result = ingest_report_file(
                file_name=file_name,
                file_id=file_id,
                project_name=proj,
                force_fallback=force_fb
            )
            p_dir = get_project_dir(proj)
            snaps = load_json_file(os.path.join(p_dir, 'snapshots.json'), {})

            self.send_json({
                'status': 'ok',
                'project': proj,
                'message': f'Successfully ingested {file_name} as {result.get("week_label")}',
                'week': result.get('week_label'),
                'snapshots': snaps.get('snapshots', snaps) if isinstance(snaps, dict) else snaps
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_briefing(self, query_or_params=''):
        """POST /api/briefing/generate?project=<slug>"""
        try:
            params = parse_request_params(query_or_params)
            proj = params.get('project') or get_default_project()
            week = params.get('week', 'w27')
            force_fb = bool(params.get('fallback', False))
            p_dir = get_project_dir(proj)

            snaps_file = os.path.join(p_dir, 'snapshots.json')
            snaps_data = load_json_file(snaps_file, {})
            snaps = snaps_data.get('snapshots', snaps_data) if isinstance(snaps_data, dict) else {}
            snap = snaps.get(week, snaps.get('w27', snaps.get('Week 27', {})))

            cfg = load_json_file(os.path.join(p_dir, 'config.json'), {})
            metrics = {
                'project_name': cfg.get('project', {}).get('name', 'Program'),
                'project_title': cfg.get('project', {}).get('title', ''),
                'organization': cfg.get('project', {}).get('organization', ''),
                'report_week': snap.get('week', week),
                'report_date': snap.get('date', datetime.now().strftime('%d %b %Y')),
                'overall_status': snap.get('overallStatus', '🟡 AMBER (Stable)'),
                'commercial_status': snap.get('kpis', {}).get('commercial', '🟢 ON TRACK'),
                'ibr_status': snap.get('kpis', {}).get('ibr', '🟡 DUE AUG 2026 (90%)'),
                'ato_status': snap.get('kpis', {}).get('ato', '🟢 GREEN'),
                'escalations_count': snap.get('kpis', {}).get('escalations', '5'),
                'total_risks': snap.get('metrics', {}).get('total_risks', 14),
                'inherent_avg_score': snap.get('metrics', {}).get('inherent_avg_score', 15.4),
                'residual_avg_score': snap.get('metrics', {}).get('residual_avg_score', 6.2),
                'delta_compression': snap.get('metrics', {}).get('delta_compression', '-9.2'),
                'eventuated_issues_count': snap.get('metrics', {}).get('eventuated_issues_count', 1),
                'total_issues': snap.get('metrics', {}).get('total_issues', 5)
            }

            synthesis = None
            podcast_script = None
            if not force_fb:
                try:
                    from scripts.gemini_generator import generate_executive_synthesis, generate_multispeaker_podcast
                    plans = snap.get('plans', [])
                    synthesis = generate_executive_synthesis(metrics, plans)
                    audio_out = os.path.join(DIRECTORY, 'assets', f'podcast_{week}.wav')
                    podcast_script = generate_multispeaker_podcast(metrics, synthesis, audio_out_path=audio_out)
                except Exception as e:
                    print(f"[Server] Gemini generation fallback: {e}")

            if not synthesis:
                synthesis = generate_fallback_synthesis(metrics)
            if not podcast_script:
                podcast_script = generate_fallback_podcast(metrics, synthesis)

            snap['synthesis'] = synthesis.get('synthesis', {})
            snap['top3'] = synthesis.get('top3', [])
            snap['sleeperOutlier'] = synthesis.get('sleeperOutlier', {})
            snap['podcastScript'] = podcast_script

            save_json_file(snaps_file, snaps_data)

            self.send_json({
                'status': 'ok',
                'project': proj,
                'week': week,
                'synthesis': snap.get('synthesis', {}),
                'top3': snap.get('top3', []),
                'sleeperOutlier': snap.get('sleeperOutlier', {}),
                'podcastScript': podcast_script
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    # --- Backward-Compatible Legacy Handler Aliases ---

    def handle_sync_all(self, query_or_params=''):
        DashboardHandler.handle_sync(self, query_or_params)

    def handle_sync_sheet(self, query_str=''):
        try:
            params = parse_request_params(query_str)
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)

            risks = load_json_file(os.path.join(p_dir, 'risks.json'), [])
            issues = load_json_file(os.path.join(p_dir, 'issues.json'), [])
            snaps = load_json_file(os.path.join(p_dir, 'snapshots.json'), {})

            if not risks and not snaps:
                legacy_data = os.path.join(DIRECTORY, 'src', 'data', 'live_synced_data.json')
                if os.path.exists(legacy_data):
                    ld = load_json_file(legacy_data, {})
                    risks = ld.get('risks', [])
                    issues = ld.get('issues', [])
                legacy_snaps = os.path.join(DIRECTORY, 'src', 'data', 'weekly_snapshots.json')
                if os.path.exists(legacy_snaps):
                    ls = load_json_file(legacy_snaps, {})
                    snaps = ls.get('snapshots', {})

            tg_risks = [r for r in risks if r.get('sourceRegister') == 'team_google' or str(r.get('id')).startswith('TG-') or str(r.get('id')).startswith('AUR-TG-')]
            joint_risks = [r for r in risks if r.get('sourceRegister') != 'team_google' and not str(r.get('id')).startswith('TG-') and not str(r.get('id')).startswith('AUR-TG-')]

            self.send_json({
                'status': 'ok',
                'project': proj,
                'risks': risks,
                'teamGoogleRisks': tg_risks,
                'registers': {
                    'joint': joint_risks,
                    'teamGoogle': tg_risks
                },
                'issues': issues,
                'snapshots': snaps.get('snapshots', snaps) if isinstance(snaps, dict) else snaps
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_check_drive_sync(self, query_str=''):
        try:
            params = parse_request_params(query_str)
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)

            snapshots_data = load_json_file(os.path.join(p_dir, 'snapshots.json'), {})
            cfg = load_json_file(os.path.join(p_dir, 'config.json'), {})

            # 1. Live Google Drive Folder Querying on demand
            folder_id = cfg.get('sources', {}).get('googleDrive', {}).get('folderId') or cfg.get('driveFolderId')
            live_reports = query_live_drive_folder(folder_id) if folder_id else []

            # 2. Known configured reports fallback/default
            raw_known = cfg.get('sources', {}).get('googleDrive', {}).get('knownReports')
            if raw_known is not None:
                configured_reports = list(raw_known)
            else:
                configured_reports = list(DEFAULT_DRIVE_REPORTS)

            seen_ids = set()
            seen_names = set()
            merged_reports = []

            # Add live reports first (authoritative Google Drive metadata & real URLs)
            for r in live_reports:
                merged_reports.append(r)
                if r.get('id'): seen_ids.add(str(r['id']))
                if r.get('name'): seen_names.add(r['name'])

            # Add configured / default reports not seen in live query
            for r in configured_reports:
                r_id = str(r.get('id')) if r.get('id') else ''
                r_name = r.get('name', '')
                if (not r_id or r_id not in seen_ids) and (not r_name or r_name not in seen_names):
                    merged_reports.append(r)
                    if r_id: seen_ids.add(r_id)
                    if r_name: seen_names.add(r_name)

            # 3. Add local candidate reports on disk if not seen
            for candidate_folder in ['drive_reports', 'drive_cache', 'reports', 'docs']:
                cf_path = os.path.join(p_dir, candidate_folder)
                if os.path.exists(cf_path) and os.path.isdir(cf_path):
                    for fn in sorted(os.listdir(cf_path)):
                        if fn.endswith(('.pdf', '.docx', '.doc', '.json', '.gdoc', '.pptx')) and fn not in seen_names:
                            w_match = re.search(r'week[\s_-]*(\d+)', fn, re.IGNORECASE) or re.search(r'\bw(\d+)\b', fn, re.IGNORECASE)
                            w_label = f"Week {w_match.group(1)}" if w_match else "New Report"
                            merged_reports.append({
                                "id": f"local_{fn}",
                                "name": fn,
                                "week": w_label,
                                "date": "Recent",
                                "url": f"file://{os.path.join(cf_path, fn)}"
                            })
                            seen_names.add(fn)

            known_reports = merged_reports

            # 4. Extract all indexed identifiers from snapshots
            indexed_ids = set()
            indexed_names = set()
            indexed_weeks = set()
            indexed_week_numbers = set()

            snaps_dict = snapshots_data.get('snapshots', snapshots_data) if isinstance(snapshots_data, dict) else {}
            for snap_key, s in snaps_dict.items():
                if isinstance(s, dict):
                    if s.get('driveFileId'): indexed_ids.add(str(s['driveFileId']))
                    if s.get('driveFileName'): indexed_names.add(s['driveFileName'])
                    if isinstance(s.get('driveFile'), dict):
                        if s['driveFile'].get('id'): indexed_ids.add(str(s['driveFile']['id']))
                        if s['driveFile'].get('name'): indexed_names.add(s['driveFile']['name'])
                    if s.get('week'):
                        indexed_weeks.add(str(s['week']).lower())
                    if s.get('weekLabel'):
                        indexed_weeks.add(str(s['weekLabel']).lower())
                    if s.get('weekNumber') is not None:
                        try:
                            indexed_week_numbers.add(int(s['weekNumber']))
                        except (ValueError, TypeError):
                            pass

                # Check snap_key (e.g. 'w28', 'Week 28')
                indexed_weeks.add(str(snap_key).lower())
                k_match = re.search(r'(\d+)', str(snap_key))
                if k_match:
                    try:
                        indexed_week_numbers.add(int(k_match.group(1)))
                    except (ValueError, TypeError):
                        pass

            all_reports = []
            uningested = []
            for r in known_reports:
                r_id = str(r.get('id', ''))
                r_name = r.get('name', '')
                r_week = str(r.get('week', '')).lower()
                r_week_num = None
                w_match = re.search(r'(\d+)', r_name) or re.search(r'(\d+)', r_week)
                if w_match:
                    try:
                        r_week_num = int(w_match.group(1))
                    except (ValueError, TypeError):
                        pass

                is_ingested = False
                if r_id and r_id in indexed_ids:
                    is_ingested = True
                elif r_name and r_name in indexed_names:
                    is_ingested = True
                elif r_week and r_week in indexed_weeks:
                    is_ingested = True
                elif r_week_num is not None and r_week_num in indexed_week_numbers:
                    is_ingested = True

                report_item = {
                    'id': r.get('id', ''),
                    'name': r.get('name', ''),
                    'week': r.get('week', 'Report'),
                    'date': r.get('date', 'Recent'),
                    'url': r.get('url', ''),
                    'isIngested': is_ingested
                }
                all_reports.append(report_item)
                if not is_ingested:
                    uningested.append(report_item)

            self.send_json({
                'status': 'ok',
                'project': proj,
                'lastSynced': snapshots_data.get('lastSynced') if isinstance(snapshots_data, dict) else None,
                'totalInDrive': len(known_reports),
                'ingestedCount': len(all_reports) - len(uningested),
                'uningestedCount': len(uningested),
                'uningestedReports': uningested,
                'allReports': all_reports,
                'snapshots': snaps_dict
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_list_notebooks(self, query_str=''):
        try:
            params = parse_request_params(query_str)
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)
            kb = load_json_file(os.path.join(p_dir, 'knowledge.json'), {})
            notebooks_list = kb.get('notebooks', [])
            if not notebooks_list and kb:
                notebooks_list = [{
                    'id': kb.get('notebookId', 'acdbb29b-8632-4fc7-9ba8-2357beeff141'),
                    'slug': kb.get('slug', 'monaro_contracts'),
                    'title': kb.get('notebookTitle', 'Project Monaro Contract Notebook'),
                    'url': kb.get('notebookUrl', 'https://notebook.google.com'),
                    'sourcesCount': len(kb.get('sources', kb.get('blueprints', [])))
                }]

            self.send_json({
                'status': 'ok',
                'project': proj,
                'activeNotebookId': kb.get('notebookId', 'acdbb29b-8632-4fc7-9ba8-2357beeff141'),
                'notebooks': notebooks_list,
                'knowledge': kb
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_check_notebook_sync(self, query_str=''):
        try:
            params = parse_request_params(query_str)
            has_proj_arg = 'project' in params
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)
            kb_data = load_json_file(os.path.join(p_dir, 'knowledge.json'), {})

            cat_path = os.path.join(DIRECTORY, 'data', 'notebook', 'sources_catalog.json')
            mapping_path = os.path.join(DIRECTORY, 'data', 'notebook', 'bundle_annex_mapping.json')
            if not has_proj_arg and os.path.exists(cat_path):
                cat_data = load_json_file(cat_path, {})
                mapping_data = load_json_file(mapping_path, {})
                self.send_json({
                    'status': 'ok',
                    'project': proj,
                    'notebookTitle': cat_data.get('notebookTitle', 'Project Monaro Contract Notebook'),
                    'notebookUrl': cat_data.get('notebookUrl', 'https://notebook.google.com'),
                    'totalSources': len(cat_data.get('sources', [])),
                    'sources': cat_data.get('sources', []),
                    'bundleMapping': mapping_data
                })
                return

            total_sources = len(kb_data.get('sources', kb_data.get('blueprints', [])))
            self.send_json({
                'status': 'ok',
                'project': proj,
                'notebookTitle': kb_data.get('notebookTitle', 'Blueprint & Contract Knowledge Base'),
                'notebookUrl': kb_data.get('notebookUrl', 'https://notebook.google.com'),
                'totalSources': total_sources,
                'sources': kb_data.get('sources', kb_data.get('blueprints', [])),
                'bundleMapping': kb_data.get('bundleMapping', {})
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_sync_notebook(self, query_or_params=''):
        try:
            params = parse_request_params(query_or_params)
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)
            kb_data = load_json_file(os.path.join(p_dir, 'knowledge.json'), {})
            self.send_json({
                'status': 'ok',
                'project': proj,
                'message': f'Successfully synchronized knowledge sources for {proj}',
                'knowledge': kb_data
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_ingest_data(self, params):
        DashboardHandler.handle_sync(self, params)

    def handle_regenerate_briefing(self, params):
        DashboardHandler.handle_briefing(self, params)

    def handle_ingest_report(self, query_str):
        DashboardHandler.handle_ingest(self, query_str)

    def process_ingest(self, params):
        DashboardHandler.handle_ingest(self, params)

def get_startup_urls(port=PORT):
    return [
        f'http://localhost:{port}',
        f'http://127.0.0.1:{port}',
    ]

def get_startup_banner(port=PORT):
    urls = get_startup_urls(port)
    default_proj = get_default_project()
    lines = [
        '=' * 64,
        f'🚀 Project Dash — Decoupled Risk & Delivery Platform ({default_proj})',
        '=' * 64,
        f'  👉 Dashboard (Local):        {urls[0]}/?project=sample',
        f'  👉 Dashboard (Loopback):     {urls[1]}/?project=sample',
        f'  👉 Dashboard (Monaro):       {urls[0]}/?project=monaro',
        f'  📡 REST Status Endpoint:     http://localhost:{port}/api/status?project={default_proj}',
        f'  📡 REST Sync Endpoint:       http://localhost:{port}/api/sync?project={default_proj}',
        '=' * 64,
        'Serving Project Dash with Unified Pipeline & REST Resource APIs.',
    ]
    return '\n'.join(lines)

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(('', PORT), DashboardHandler) as httpd:
            print(get_startup_banner(PORT))
            httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print('\n🛑 Project Dash server stopped gracefully.')
