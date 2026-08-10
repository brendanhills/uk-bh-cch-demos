import sys
import os
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Automatically load .env file if present
env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_file):
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))
    except Exception:
        pass

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 9000
DEBUG_MODE = any("debug=1" in arg or "--debug" in arg for arg in sys.argv)

active_evolution_process = None

def stop_evolution_process():
    global active_evolution_process
    if active_evolution_process and active_evolution_process.poll() is None:
        sys.stdout.write("\033[33m[ALPHAEVOLVE]\033[0m Stopping running AlphaEvolve process...\n")
        sys.stdout.flush()
        try:
            active_evolution_process.terminate()
            active_evolution_process.wait(timeout=3)
        except Exception:
            try:
                active_evolution_process.kill()
            except Exception:
                pass
        active_evolution_process = None

class DemoRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/cch/data/"):
            self.path = self.path.replace("/cch/data/", "/data/")
        elif self.path.startswith("/cch/fixtures/"):
            self.path = self.path.replace("/cch/fixtures/", "/fixtures/")

        if self.path.startswith("/fixtures/traces_"):
            self.path = self.path.replace("/fixtures/traces_", "/data/traces_")

        if (self.path == "/cch/" or self.path.startswith("/cch/index.html") or self.path == "/rch/" or self.path.startswith("/rch/index.html")) and DEBUG_MODE:
            try:
                html_path = os.path.join(os.path.dirname(__file__), "cch", "index.html")
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("</head>", "<script>window.SERVER_DEBUG = 1;</script></head>")
                encoded = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return
            except Exception:
                pass
        super().do_GET()
    def log_message(self, format, *args):
        # Silence standard HTTP 200 & 304 GET access logs to keep terminal output clean
        request_line = str(args[0]) if len(args) > 0 else ""
        status_code = str(args[1]) if len(args) > 1 else "200"

        # Suppress 200/304 HTTP logs (only print server errors >= 400)
        if str(status_code) in ("200", "304"):
            return

        # Print formatted server log for errors/warnings
        sys.stdout.write(f"\033[36m[CCH SERVER]\033[0m {self.address_string()} - {request_line} [{status_code}]\n")
        sys.stdout.flush()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self):
        global active_evolution_process
        if self.path == "/run-optimization":
            stop_evolution_process()
            sys.stdout.write("\033[32m[ALPHAEVOLVE]\033[0m Triggering Live Optimization Run (traces_dynamic.jsonl)...\n")
            sys.stdout.flush()
            # Truncate candidates_feed.jsonl for clean live run
            try:
                feed_path = os.path.join(os.path.dirname(__file__), "data", "candidates_feed.jsonl")
                with open(feed_path, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception as e:
                sys.stdout.write(f"\033[31m[ALPHAEVOLVE]\033[0m Could not truncate candidates_feed.jsonl: {e}\n")

            # Fire the loop asynchronously in a background subprocess
            active_evolution_process = subprocess.Popen([
                "uv", "run", "python", "-u", "experiment/run_evolution.py"
            ], env=dict(
                os.environ, 
                TRACE_FILENAME="traces_dynamic.jsonl", 
                SCENARIO="standard",
                MODEL=os.getenv("MODEL", "gemini-3.5-flash")
            ))
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status": "started", "trace": "traces_dynamic.jsonl"}')
        elif self.path == "/stop-optimization":
            stop_evolution_process()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status": "stopped"}')
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_OPTIONS(self):
        # Support CORS preflight if needed
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

import threading
import time
import json

def watch_candidate_feed():
    """Tails data/candidates_feed.jsonl and streams search progress to server stdout."""
    feed_path = os.path.join(os.path.dirname(__file__), "data", "candidates_feed.jsonl")
    seen_pos = os.path.getsize(feed_path) if os.path.exists(feed_path) else 0
    while True:
        try:
            if os.path.exists(feed_path):
                file_size = os.path.getsize(feed_path)
                if file_size < seen_pos:
                    seen_pos = 0
                with open(feed_path, "r") as f:
                    f.seek(seen_pos)
                    lines = f.readlines()
                    seen_pos = f.tell()
                    for line in lines:
                        if line.strip():
                            data = json.loads(line.strip())
                            cand_id = data.get("id", "?")
                            status = data.get("status", "SEARCHING")
                            title = data.get("title", "")
                            score = data.get("score", 0.0)
                            summary = data.get("summary", "")
                            color = "\033[32m" if status in ("ACCEPTED", "BASELINE", "REPLANNED") else ("\033[31m" if status == "REJECTED" else "\033[33m")
                            sys.stdout.write(f"{color}[ALPHAEVOLVE {status}]\033[0m Candidate {cand_id}: {title} | Score: {score:,.1f}\n")
                            if summary:
                                sys.stdout.write(f"                   💡 {summary}\n")
                            sys.stdout.flush()
        except Exception:
            pass
        time.sleep(1.0)

threading.Thread(target=watch_candidate_feed, daemon=True).start()

print("\033[1;34m--------------------------------------------------\033[0m")
print(f"\033[1;32m[CCH DEMO SERVER]\033[0m Running on http://localhost:{PORT}/cch/")
print(f"\033[1;30m[KMART RETAIL DEMO]\033[0m Running on http://localhost:{PORT}/legacy_kmart/ui/")
print("\033[1;34m--------------------------------------------------\033[0m")

httpd = HTTPServer(("", PORT), DemoRequestHandler)
httpd.serve_forever()
