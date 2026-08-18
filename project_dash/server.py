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

PORT = 9000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
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
    p_dir = os.path.join(DIRECTORY, 'data', project_slug)
    if os.path.exists(p_dir):
        return p_dir
    # Fallback to sample
    sample_dir = os.path.join(DIRECTORY, 'data', 'sample')
    if os.path.exists(sample_dir):
        return sample_dir
    return os.path.join(DIRECTORY, 'data')

# Default fallback Drive folder reports
DEFAULT_DRIVE_REPORTS = [
    {"id": "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu", "week": "Week 27", "date": "07 Aug 2026", "name": "Weekly Reporting - Week 27 - 07 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu/view"},
    {"id": "1UlQmROLEbOroFI8neyne3qOUm4wEgCyC", "week": "Week 26", "date": "31 Jul 2026", "name": "Weekly Reporting - Week 26 - 31 Jul 2026.pdf", "url": "https://drive.google.com/file/d/1UlQmROLEbOroFI8neyne3qOUm4wEgCyC/view"},
    {"id": "13ThXt0QIpS2OFg4NEewfx8ggoD2CItlz", "week": "Week 25", "date": "24 Jul 2026", "name": "Weekly Reporting - Week 25 - 24 Jul 2026.pdf", "url": "https://drive.google.com/file/d/13ThXt0QIpS2OFg4NEewfx8ggoD2CItlz/view"},
    {"id": "100xnsVUDdlKVzxTgK26_lmjSYYUWnUhK", "week": "Week 24", "date": "17 Jul 2026", "name": "Weekly Reporting - Week 24 - 17 Jul 2026.pdf", "url": "https://drive.google.com/file/d/100xnsVUDdlKVzxTgK26_lmjSYYUWnUhK/view"},
    {"id": "1YRJuXlIIkYRYEsU41K_nuO9iIwrS9k0e", "week": "Week 23", "date": "10 Jul 2026", "name": "Weekly Reporting - Week 23 - 10 Jul 2026.pdf", "url": "https://drive.google.com/file/d/1YRJuXlIIkYRYEsU41K_nuO9iIwrS9k0e/view"},
    {"id": "1kQiDQPF9DCUZ0vvbivToMoJWeZJoB0eREFnywRxpCHA", "week": "Week 22", "date": "03 Jul 2026", "name": "Weekly Reporting - Week 22 - 03 Jul 2026 (Google Doc)", "url": "https://docs.google.com/document/d/1kQiDQPF9DCUZ0vvbivToMoJWeZJoB0eREFnywRxpCHA/edit"}
]

KNOWN_DRIVE_REPORTS = DEFAULT_DRIVE_REPORTS

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

        if parsed.path == '/api/ingest-data':
            self.handle_ingest_data(params)
        elif parsed.path == '/api/regenerate-briefing':
            self.handle_regenerate_briefing(params)
        elif parsed.path == '/api/ingest-report':
            self.process_ingest(params)
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

    def handle_sync_sheet(self, query_str=''):
        try:
            params = urllib.parse.parse_qs(query_str) if query_str else {}
            proj = params.get('project', [get_default_project()])[0]
            p_dir = get_project_dir(proj)

            risks = []
            issues = []
            snapshots = {}

            risks_file = os.path.join(p_dir, 'risks.json')
            if os.path.exists(risks_file):
                with open(risks_file, 'r', encoding='utf-8') as f:
                    r_data = json.load(f)
                    risks = r_data if isinstance(r_data, list) else r_data.get('risks', [])

            issues_file = os.path.join(p_dir, 'issues.json')
            if os.path.exists(issues_file):
                with open(issues_file, 'r', encoding='utf-8') as f:
                    i_data = json.load(f)
                    issues = i_data if isinstance(i_data, list) else i_data.get('issues', [])

            snaps_file = os.path.join(p_dir, 'snapshots.json')
            if os.path.exists(snaps_file):
                with open(snaps_file, 'r', encoding='utf-8') as f:
                    s_data = json.load(f)
                    snapshots = s_data.get('snapshots', s_data) if isinstance(s_data, dict) else {}

            if not risks and not snapshots:
                legacy_data = os.path.join(DIRECTORY, 'src', 'data', 'live_synced_data.json')
                if os.path.exists(legacy_data):
                    with open(legacy_data, 'r', encoding='utf-8') as f:
                        ld = json.load(f)
                        risks = ld.get('risks', [])
                        issues = ld.get('issues', [])
                legacy_snaps = os.path.join(DIRECTORY, 'src', 'data', 'weekly_snapshots.json')
                if os.path.exists(legacy_snaps):
                    with open(legacy_snaps, 'r', encoding='utf-8') as f:
                        ls = json.load(f)
                        snapshots = ls.get('snapshots', {})

            tg_risks = [r for r in risks if r.get('sourceRegister') == 'team_google' or str(r.get('id')).startswith('TG-') or str(r.get('id')).startswith('AUR-TG-')]
            joint_risks = [r for r in risks if r.get('sourceRegister') != 'team_google' and not str(r.get('id')).startswith('TG-') and not str(r.get('id')).startswith('AUR-TG-')]

            response = {
                'status': 'ok',
                'project': proj,
                'risks': risks,
                'teamGoogleRisks': tg_risks,
                'registers': {
                    'joint': joint_risks,
                    'teamGoogle': tg_risks
                },
                'issues': issues,
                'snapshots': snapshots
            }
            self.send_json(response)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_check_drive_sync(self, query_str=''):
        try:
            params = urllib.parse.parse_qs(query_str) if query_str else {}
            proj = params.get('project', [get_default_project()])[0]
            p_dir = get_project_dir(proj)

            snaps_file = os.path.join(p_dir, 'snapshots.json')
            snapshots_data = {}
            if os.path.exists(snaps_file):
                with open(snaps_file, 'r', encoding='utf-8') as f:
                    snapshots_data = json.load(f)

            cfg_file = os.path.join(p_dir, 'config.json')
            known_reports = DEFAULT_DRIVE_REPORTS
            if os.path.exists(cfg_file):
                with open(cfg_file, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    drive_src = cfg.get('sources', {}).get('googleDrive', {})
                    if drive_src.get('knownReports'):
                        known_reports = drive_src['knownReports']

            indexed_ids = set()
            snaps_dict = snapshots_data.get('snapshots', snapshots_data) if isinstance(snapshots_data, dict) else {}
            for s in snaps_dict.values():
                if isinstance(s, dict):
                    if s.get('driveFileId'): indexed_ids.add(s['driveFileId'])
                    if s.get('driveFileName'): indexed_ids.add(s['driveFileName'])

            all_reports = []
            uningested = []
            for r in known_reports:
                is_ingested = (r['id'] in indexed_ids) or (r['name'] in indexed_ids)
                report_item = {
                    'id': r['id'],
                    'name': r['name'],
                    'week': r['week'],
                    'date': r['date'],
                    'url': r['url'],
                    'isIngested': is_ingested
                }
                all_reports.append(report_item)
                if not is_ingested:
                    uningested.append(report_item)

            response = {
                'status': 'ok',
                'project': proj,
                'lastSynced': snapshots_data.get('lastSynced') if isinstance(snapshots_data, dict) else None,
                'totalInDrive': len(known_reports),
                'ingestedCount': len(all_reports) - len(uningested),
                'uningestedCount': len(uningested),
                'uningestedReports': uningested,
                'allReports': all_reports,
                'snapshots': snaps_dict
            }
            self.send_json(response)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_list_notebooks(self, query_str=''):
        try:
            params = urllib.parse.parse_qs(query_str) if query_str else {}
            proj = params.get('project', [get_default_project()])[0]
            p_dir = get_project_dir(proj)

            kb_file = os.path.join(p_dir, 'knowledge.json')
            kb = {}
            if os.path.exists(kb_file):
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb = json.load(f)

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
            params = urllib.parse.parse_qs(query_str) if query_str else {}
            has_proj_arg = 'project' in params
            proj = params.get('project', [get_default_project()])[0]
            p_dir = get_project_dir(proj)

            kb_file = os.path.join(p_dir, 'knowledge.json')
            kb_data = {}
            if os.path.exists(kb_file):
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)

            cat_path = os.path.join(DIRECTORY, 'data', 'notebook', 'sources_catalog.json')
            mapping_path = os.path.join(DIRECTORY, 'data', 'notebook', 'bundle_annex_mapping.json')
            if not has_proj_arg and os.path.exists(cat_path):
                with open(cat_path, 'r', encoding='utf-8') as f:
                    cat_data = json.load(f)
                mapping_data = {}
                if os.path.exists(mapping_path):
                    with open(mapping_path, 'r', encoding='utf-8') as f:
                        mapping_data = json.load(f)
                response = {
                    'status': 'ok',
                    'project': proj,
                    'notebookTitle': cat_data.get('notebookTitle', 'Project Monaro Contract Notebook'),
                    'notebookUrl': cat_data.get('notebookUrl', 'https://notebook.google.com'),
                    'totalSources': len(cat_data.get('sources', [])),
                    'sources': cat_data.get('sources', []),
                    'bundleMapping': mapping_data
                }
                self.send_json(response)
                return

            total_sources = len(kb_data.get('sources', kb_data.get('blueprints', [])))
            response = {
                'status': 'ok',
                'project': proj,
                'notebookTitle': kb_data.get('notebookTitle', 'Blueprint & Contract Knowledge Base'),
                'notebookUrl': kb_data.get('notebookUrl', 'https://notebook.google.com'),
                'totalSources': total_sources,
                'sources': kb_data.get('sources', kb_data.get('blueprints', [])),
                'bundleMapping': kb_data.get('bundleMapping', {})
            }
            self.send_json(response)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_sync_notebook(self, query_or_params=''):
        try:
            if isinstance(query_or_params, dict):
                params = query_or_params
            else:
                q = urllib.parse.parse_qs(query_or_params) if query_or_params else {}
                params = {k: v[0] for k, v in q.items()}

            proj = params.get('project', get_default_project())
            p_dir = get_project_dir(proj)

            ingest_script = os.path.join(DIRECTORY, 'scripts', 'ingest_data.py')
            cmd = [sys.executable, ingest_script, f'--project={proj}']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=DIRECTORY)

            kb_file = os.path.join(p_dir, 'knowledge.json')
            kb_data = {}
            if os.path.exists(kb_file):
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)

            self.send_json({
                'status': 'ok',
                'project': proj,
                'message': f'Successfully synchronized knowledge sources for {proj}',
                'knowledge': kb_data
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_ingest_data(self, params):
        try:
            proj = params.get('project', get_default_project())
            p_dir = get_project_dir(proj)

            ingest_script = os.path.join(DIRECTORY, 'scripts', 'ingest_data.py')
            cmd = [sys.executable, ingest_script, f'--project={proj}']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=DIRECTORY)

            if result.returncode != 0:
                self.send_json({'error': result.stderr or 'Ingestion script execution failed'}, 500)
                return

            self.send_json({
                'status': 'ok',
                'project': proj,
                'message': f'Successfully ingested project {proj}'
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_regenerate_briefing(self, params):
        try:
            proj = params.get('project', get_default_project())
            week = params.get('week', 'w27')
            p_dir = get_project_dir(proj)

            snaps_file = os.path.join(p_dir, 'snapshots.json')
            snaps_data = {}
            if os.path.exists(snaps_file):
                with open(snaps_file, 'r', encoding='utf-8') as f:
                    snaps_data = json.load(f)

            snaps = snaps_data.get('snapshots', snaps_data)
            snap = snaps.get(week, snaps.get('w27', {}))

            try:
                from scripts.gemini_generator import generate_executive_synthesis
                cfg_file = os.path.join(p_dir, 'config.json')
                cfg = {}
                if os.path.exists(cfg_file):
                    with open(cfg_file, 'r', encoding='utf-8') as f:
                        cfg = json.load(f)

                metrics = {
                    'project_name': cfg.get('project', {}).get('name', 'Program'),
                    'project_title': cfg.get('project', {}).get('title', ''),
                    'organization': cfg.get('project', {}).get('organization', ''),
                    'report_week': snap.get('week', 'Week 27'),
                    'report_date': snap.get('date', '07 Aug 2026'),
                    'overall_status': snap.get('overallStatus', '🟡 AMBER (Stable)'),
                    'commercial_status': snap.get('kpis', {}).get('commercial', '🟢 ON TRACK'),
                    'ibr_status': snap.get('kpis', {}).get('ibr', '🟡 DUE AUG 2026 (90%)'),
                    'ato_status': snap.get('kpis', {}).get('ato', '🟢 GREEN'),
                    'escalations_count': snap.get('kpis', {}).get('escalations', '5'),
                }
                plans = snap.get('plans', [])
                synthesis_result = generate_executive_synthesis(metrics, plans)
                if synthesis_result and isinstance(synthesis_result, dict):
                    if synthesis_result.get('paragraphs'):
                        snap['synthesis'] = synthesis_result['paragraphs']
                    if synthesis_result.get('top3'):
                        snap['top3'] = synthesis_result['top3']
                    if synthesis_result.get('sleeperOutlier'):
                        snap['sleeperOutlier'] = synthesis_result['sleeperOutlier']

                    with open(snaps_file, 'w', encoding='utf-8') as f:
                        json.dump(snaps_data, f, indent=2)
            except Exception as gen_err:
                print(f'[Server] Gemini regeneration fallback: {gen_err}')

            self.send_json({
                'status': 'ok',
                'project': proj,
                'week': week,
                'synthesis': snap.get('synthesis', {}),
                'top3': snap.get('top3', []),
                'sleeperOutlier': snap.get('sleeperOutlier', {})
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_ingest_report(self, query_str):
        params = urllib.parse.parse_qs(query_str) if query_str else {}
        file_id = params.get('file_id', [''])[0]
        file_name = params.get('file_name', [''])[0]
        proj = params.get('project', [get_default_project()])[0]
        self.process_ingest({'file_id': file_id, 'file_name': file_name, 'project': proj})

    def process_ingest(self, params):
        try:
            file_id = params.get('file_id') or 'new-drive-file'
            file_name = params.get('file_name') or 'Weekly Reporting - Week 27 - 07 Aug 2026.pdf'
            proj = params.get('project') or get_default_project()
            p_dir = get_project_dir(proj)

            script_path = os.path.join(DIRECTORY, 'scripts', 'ingest_weekly_report.py')
            cmd = [sys.executable, script_path, '--file-id', file_id, '--name', file_name, '--project', proj]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=DIRECTORY)

            snaps_file = os.path.join(p_dir, 'snapshots.json')
            updated = {}
            if os.path.exists(snaps_file):
                with open(snaps_file, 'r', encoding='utf-8') as f:
                    updated = json.load(f)

            if result.returncode == 0:
                self.send_json({
                    'status': 'ok',
                    'project': proj,
                    'message': f'Successfully ingested {file_name}',
                    'snapshots': updated.get('snapshots', updated) if isinstance(updated, dict) else {}
                })
            else:
                self.send_json({'error': result.stderr or 'Ingestion script failed'}, 500)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

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
        f'  👉 Dashboard (Proprietary):  {urls[0]}/?project=f-dse',
        f'  📡 API Sync Endpoint:        http://localhost:{port}/api/sync-sheet?project={default_proj}',
        '=' * 64,
        'Serving Project Dash with Decoupled Datasets & On-Demand APIs.',
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
