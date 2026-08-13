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
SNAPSHOTS_FILE = os.path.join(DIRECTORY, "src", "data", "weekly_snapshots.json")

# Pre-known Drive folder reports (representing live folder content)
KNOWN_DRIVE_REPORTS = [
    {"id": "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu", "week": "Week 27", "date": "07 Aug 2026", "name": "Weekly Reporting - Week 27 - 07 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu/view"},
    {"id": "1UlQmROLEbOroFI8neyne3qOUm4wEgCyC", "week": "Week 26", "date": "31 Jul 2026", "name": "Weekly Reporting - Week 26 - 31 Jul 2026.pdf", "url": "https://drive.google.com/file/d/1UlQmROLEbOroFI8neyne3qOUm4wEgCyC/view"},
    {"id": "13ThXt0QIpS2OFg4NEewfx8ggoD2CItlz", "week": "Week 25", "date": "24 Jul 2026", "name": "Weekly Reporting - Week 25 - 24 Jul 2026.pdf", "url": "https://drive.google.com/file/d/13ThXt0QIpS2OFg4NEewfx8ggoD2CItlz/view"},
    {"id": "100xnsVUDdlKVzxTgK26_lmjSYYUWnUhK", "week": "Week 24", "date": "17 Jul 2026", "name": "Weekly Reporting - Week 24 - 17 Jul 2026.pdf", "url": "https://drive.google.com/file/d/100xnsVUDdlKVzxTgK26_lmjSYYUWnUhK/view"},
    {"id": "1YRJuXlIIkYRYEsU41K_nuO9iIwrS9k0e", "week": "Week 23", "date": "10 Jul 2026", "name": "Weekly Reporting - Week 23 - 10 Jul 2026.pdf", "url": "https://drive.google.com/file/d/1YRJuXlIIkYRYEsU41K_nuO9iIwrS9k0e/view"},
    {"id": "1kQiDQPF9DCUZ0vvbivToMoJWeZJoB0eREFnywRxpCHA", "week": "Week 22", "date": "03 Jul 2026", "name": "Weekly Reporting - Week 22 - 03 Jul 2026 (Google Doc)", "url": "https://docs.google.com/document/d/1kQiDQPF9DCUZ0vvbivToMoJWeZJoB0eREFnywRxpCHA/edit"}
]

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
        if parsed.path == '/api/sync-sheet':
            self.handle_sync_sheet()
        elif parsed.path == '/api/check-drive-sync':
            self.handle_check_drive_sync()
        elif parsed.path == '/api/check-notebook-sync':
            self.handle_check_notebook_sync()
        elif parsed.path == '/api/sync-notebook':
            self.handle_sync_notebook()
        elif parsed.path == '/api/ingest-report':
            self.handle_ingest_report(parsed.query)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/ingest-report':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            params = json.loads(body) if body else {}
            self.process_ingest(params)
        elif parsed.path == '/api/sync-notebook':
            self.handle_sync_notebook()
        else:
            super().do_POST()

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def handle_sync_sheet(self):
        try:
            data_path = os.path.join(DIRECTORY, "src", "data", "live_synced_data.json")
            if os.path.exists(data_path):
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"status": "ok", "risks": [], "issues": []}

            if os.path.exists(SNAPSHOTS_FILE):
                with open(SNAPSHOTS_FILE, 'r', encoding='utf-8') as sf:
                    snap_data = json.load(sf)
                    data['snapshots'] = snap_data.get('snapshots', {})

            self.send_json(data)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    
    def handle_check_notebook_sync(self):
        try:
            cat_path = os.path.join(DIRECTORY, "data", "notebook", "sources_catalog.json")
            mapping_path = os.path.join(DIRECTORY, "data", "notebook", "bundle_annex_mapping.json")
            cat_data = {}
            mapping_data = {}
            if os.path.exists(cat_path):
                with open(cat_path, "r", encoding="utf-8") as f:
                    cat_data = json.load(f)
            if os.path.exists(mapping_path):
                with open(mapping_path, "r", encoding="utf-8") as f:
                    mapping_data = json.load(f)

            response = {
                "status": "ok",
                "notebookId": cat_data.get("notebookId", "acdbb29b-8632-4fc7-9ba8-2357beeff141"),
                "notebookTitle": cat_data.get("notebookTitle", "Project Monaro Contract Notebook"),
                "notebookUrl": cat_data.get("notebookUrl", "https://notebook.google.com/notebook/acdbb29b-8632-4fc7-9ba8-2357beeff141"),
                "lastSynced": cat_data.get("lastSynced"),
                "totalSources": cat_data.get("totalSources", len(cat_data.get("sources", []))),
                "sources": cat_data.get("sources", []),
                "bundleMapping": mapping_data
            }
            self.send_json(response)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_sync_notebook(self):
        try:
            script_path = os.path.join(DIRECTORY, "scripts", "sync_notebook.py")
            cmd = [sys.executable, script_path]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=DIRECTORY)

            if result.returncode == 0:
                cat_path = os.path.join(DIRECTORY, "data", "notebook", "sources_catalog.json")
                mapping_path = os.path.join(DIRECTORY, "data", "notebook", "bundle_annex_mapping.json")
                with open(cat_path, "r", encoding="utf-8") as f:
                    cat_data = json.load(f)
                with open(mapping_path, "r", encoding="utf-8") as f:
                    mapping_data = json.load(f)
                self.send_json({
                    "status": "ok",
                    "message": "Successfully synchronized Gemini Notebook sources and bundle mappings",
                    "catalog": cat_data,
                    "bundleMapping": mapping_data
                })
            else:
                self.send_json({"error": result.stderr or "Sync notebook script failed"}, 500)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_check_drive_sync(self):
        try:
            snapshots_data = {}
            if os.path.exists(SNAPSHOTS_FILE):
                with open(SNAPSHOTS_FILE, 'r', encoding='utf-8') as f:
                    snapshots_data = json.load(f)

            indexed_ids = set()
            for s in snapshots_data.get('snapshots', {}).values():
                if s.get('driveFileId'):
                    indexed_ids.add(s['driveFileId'])
                if s.get('driveFileName'):
                    indexed_ids.add(s['driveFileName'])

            all_reports = []
            uningested = []
            
            for r in KNOWN_DRIVE_REPORTS:
                is_ingested = (r['id'] in indexed_ids) or (r['name'] in indexed_ids)
                report_item = {
                    "id": r['id'],
                    "name": r['name'],
                    "week": r['week'],
                    "date": r['date'],
                    "url": r['url'],
                    "isIngested": is_ingested
                }
                all_reports.append(report_item)
                if not is_ingested:
                    uningested.append(report_item)

            response = {
                "status": "ok",
                "lastSynced": snapshots_data.get('lastSynced'),
                "totalInDrive": len(KNOWN_DRIVE_REPORTS),
                "ingestedCount": len(all_reports) - len(uningested),
                "uningestedCount": len(uningested),
                "uningestedReports": uningested,
                "allReports": all_reports,
                "snapshots": snapshots_data.get('snapshots', {})
            }
            self.send_json(response)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_ingest_report(self, query_str):
        params = urllib.parse.parse_qs(query_str)
        file_id = params.get('file_id', [''])[0]
        file_name = params.get('file_name', [''])[0]
        self.process_ingest({"file_id": file_id, "file_name": file_name})

    def process_ingest(self, params):
        try:
            file_id = params.get('file_id') or 'new-drive-file'
            file_name = params.get('file_name') or 'Weekly Reporting - Week 27 - 07 Aug 2026.pdf'
            
            script_path = os.path.join(DIRECTORY, "scripts", "ingest_weekly_report.py")
            cmd = [sys.executable, script_path, "--file-id", file_id, "--name", file_name]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=DIRECTORY)

            if result.returncode == 0:
                with open(SNAPSHOTS_FILE, 'r', encoding='utf-8') as f:
                    updated = json.load(f)
                self.send_json({
                    "status": "ok",
                    "message": f"Successfully ingested {file_name}",
                    "snapshots": updated.get('snapshots', {})
                })
            else:
                self.send_json({"error": result.stderr or "Ingestion script failed"}, 500)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

def get_startup_urls(port=PORT):
    """Return the list of clickable URLs for accessing the dashboard."""
    return [
        f"http://localhost:{port}",
        f"http://127.0.0.1:{port}",
    ]

def get_startup_banner(port=PORT):
    """Format and return the startup banner with clickable URLs."""
    urls = get_startup_urls(port)
    lines = [
        "=" * 64,
        "🚀 F-DSE Program Governance & Risk Intelligence Platform",
        "=" * 64,
        f"  👉 Dashboard URL (Local):    {urls[0]}",
        f"  👉 Dashboard URL (Loopback): {urls[1]}",
        f"  📡 API Sync Endpoint:        http://localhost:{port}/api/sync-sheet",
        f"  📁 Drive Sync Endpoint:      http://localhost:{port}/api/check-drive-sync",
        "=" * 64,
        "Serving Project Dash with Drive Ingestion & Sync API. Press Ctrl+C to stop.",
    ]
    return "\n".join(lines)

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            print(get_startup_banner(PORT))
            httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Project Dash server stopped gracefully.")

