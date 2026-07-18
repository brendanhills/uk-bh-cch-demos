#!/usr/bin/env python3
"""
Live Translate Demo - Real-Time Bidirectional Bilingual Medical Interpreter Forwarder.
This root-level script has been consolidated into the central `demo/web_server.py` engine
and forwards all arguments transparently with the `--cli` flag enabled.
"""

import sys
import subprocess

def main():
    cmd = ["uv", "run", "demo/web_server.py", "--cli"] + sys.argv[1:]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
