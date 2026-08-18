#!/usr/bin/env python3
"""
check_build_status.py — Query Google Cloud Build status and extract failure diagnostics.

Usage:
  python3 scripts/check_build_status.py
  python3 scripts/check_build_status.py --project monaro-risk-dev --region us-central1
  python3 scripts/check_build_status.py --build-id <BUILD_ID>
  python3 scripts/check_build_status.py --limit 5
  python3 scripts/check_build_status.py --json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime


# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_gcloud_cmd(cmd_list):
    """Run a gcloud command and return (stdout, returncode, stderr)."""
    try:
        res = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            check=False
        )
        return res.stdout, res.returncode, res.stderr
    except FileNotFoundError:
        print(f"{RED}Error: 'gcloud' CLI is not installed or not found in PATH.{RESET}")
        sys.exit(1)


def get_recent_builds(project="monaro-risk-dev", region="us-central1", limit=1):
    """Fetch the most recent Cloud Build metadata."""
    cmd = [
        "gcloud", "builds", "list",
        f"--project={project}",
        f"--billing-project={project}",
        f"--region={region}",
        f"--limit={limit}",
        "--format=json"
    ]
    stdout, code, stderr = run_gcloud_cmd(cmd)
    if code != 0:
        print(f"{RED}Failed to query Cloud Build API:{RESET}\n{stderr.strip()}")
        sys.exit(code)
    
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        print(f"{RED}Failed to parse gcloud output as JSON.{RESET}")
        sys.exit(1)


def get_build_details(build_id, project="monaro-risk-dev", region="us-central1"):
    """Fetch full details of a specific build."""
    cmd = [
        "gcloud", "builds", "describe", build_id,
        f"--project={project}",
        f"--billing-project={project}",
        f"--region={region}",
        "--format=json"
    ]
    stdout, code, stderr = run_gcloud_cmd(cmd)
    if code != 0:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def get_build_logs(build_id, project="monaro-risk-dev", region="us-central1", tail_lines=40):
    """Fetch build logs for a build."""
    cmd = [
        "gcloud", "builds", "log", build_id,
        f"--project={project}",
        f"--billing-project={project}",
        f"--region={region}"
    ]
    stdout, _, stderr = run_gcloud_cmd(cmd)
    output = stdout or stderr or ""
    lines = output.strip().splitlines()
    if len(lines) > tail_lines:
        return "\n".join(lines[-tail_lines:])
    return output.strip()


def format_timestamp(iso_str):
    """Convert ISO timestamp to human-friendly local string."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return iso_str


def inspect_build(build, project, region):
    """Inspect and display build status and diagnostics."""
    build_id = build.get("id", "Unknown")
    status = build.get("status", "UNKNOWN")
    create_time = format_timestamp(build.get("createTime"))
    finish_time = format_timestamp(build.get("finishTime"))
    
    subs = build.get("substitutions", {})
    commit_sha = subs.get("COMMIT_SHA", build.get("sourceProvenance", {}).get("resolvedGitSource", {}).get("revision", "N/A"))
    short_sha = commit_sha[:7] if commit_sha and commit_sha != "N/A" else "N/A"
    branch = subs.get("BRANCH_NAME", subs.get("REF_NAME", "dev"))
    trigger_name = subs.get("TRIGGER_NAME", "N/A")
    log_url = build.get("logUrl", "")

    status_icon = "🟢" if status == "SUCCESS" else ("🔴" if status in ("FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED") else "⏳")
    status_color = GREEN if status == "SUCCESS" else (RED if status in ("FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED") else YELLOW)

    print(f"\n{BOLD}══════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}Google Cloud Build Status — {CYAN}{project}{RESET} ({region})")
    print(f"{BOLD}══════════════════════════════════════════════════════════════════════{RESET}")
    print(f"  {BOLD}Build ID:{RESET}       {build_id}")
    print(f"  {BOLD}Status:{RESET}         {status_icon} {status_color}{BOLD}{status}{RESET}")
    print(f"  {BOLD}Trigger:{RESET}        {trigger_name} ({branch} branch)")
    print(f"  {BOLD}Commit:{RESET}         {short_sha} ({commit_sha})")
    print(f"  {BOLD}Created:{RESET}        {create_time}")
    print(f"  {BOLD}Finished:{RESET}       {finish_time}")
    if log_url:
        print(f"  {BOLD}Console URL:{RESET}    {BLUE}{log_url}{RESET}")
    print(f"{BOLD}──────────────────────────────────────────────────────────────────────{RESET}")

    # Inspect Steps
    steps = build.get("steps", [])
    if steps:
        print(f"\n{BOLD}Pipeline Steps Summary:{RESET}")
        for idx, step in enumerate(steps):
            step_name = step.get("name", "unknown")
            step_status = step.get("status", "QUEUED")
            step_exit = step.get("exitCode", None)
            
            s_icon = "✅" if step_status == "SUCCESS" else ("❌" if step_status == "FAILURE" else ("⏳" if step_status == "WORKING" else "⚪"))
            s_color = GREEN if step_status == "SUCCESS" else (RED if step_status == "FAILURE" else (YELLOW if step_status == "WORKING" else RESET))
            
            step_desc = f"Step #{idx} ({step_name})"
            if step.get("dir"):
                step_desc += f" [dir: {step.get('dir')}]"
            
            status_text = f"{s_color}{step_status}{RESET}"
            if step_exit is not None and step_exit != 0:
                status_text += f" {RED}(Exit code: {step_exit}){RESET}"
                
            print(f"  {s_icon} {step_desc:<55} → {status_text}")

    # If build failed, print detailed failure diagnostics and logs
    if status in ("FAILURE", "TIMEOUT", "INTERNAL_ERROR"):
        print(f"\n{RED}{BOLD}🚨 BUILD FAILURE DIAGNOSTICS:{RESET}")
        failure_info = build.get("failureInfo", {})
        if failure_info:
            print(f"  {BOLD}Failure Type:{RESET}   {failure_info.get('type', 'N/A')}")
            print(f"  {BOLD}Detail:{RESET}         {failure_info.get('detail', 'N/A')}")
        
        # Find failed step
        failed_step = next((s for s in steps if s.get("status") == "FAILURE"), None)
        if failed_step:
            print(f"\n  {BOLD}Failed Step Container:{RESET} {failed_step.get('name')}")
            args = failed_step.get("args", [])
            if args:
                args_str = " ".join(args) if isinstance(args, list) else str(args)
                print(f"  {BOLD}Executed Command:{RESET}      {args_str[:120]}...")

        print(f"\n{BOLD}📋 Tail Build Logs (Last 30 lines):{RESET}")
        print(f"{RED}──────────────────────────────────────────────────────────────────────{RESET}")
        logs = get_build_logs(build_id, project, region, tail_lines=30)
        print(logs)
        print(f"{RED}──────────────────────────────────────────────────────────────────────{RESET}")
    else:
        print(f"\n{GREEN}{BOLD}✨ Build succeeded! Cloud Run service revision was deployed.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Check Google Cloud Build status and extract diagnostics.")
    parser.add_argument("--project", default="monaro-risk-dev", help="GCP project ID (default: monaro-risk-dev)")
    parser.add_argument("--region", default="us-central1", help="GCP region (default: us-central1)")
    parser.add_argument("--build-id", default=None, help="Specific build ID to inspect")
    parser.add_argument("--limit", type=int, default=1, help="Number of recent builds to list/inspect (default: 1)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON data")

    args = parser.parse_args()

    if args.build_id:
        build = get_build_details(args.build_id, args.project, args.region)
        if not build:
            print(f"{RED}Build {args.build_id} not found in project {args.project}.{RESET}")
            sys.exit(1)
        builds = [build]
    else:
        builds = get_recent_builds(args.project, args.region, args.limit)

    if args.json:
        print(json.dumps(builds, indent=2))
        return

    if not builds:
        print(f"{YELLOW}No builds found for project {args.project} in region {args.region}.{RESET}")
        return

    for build in builds:
        inspect_build(build, args.project, args.region)


if __name__ == "__main__":
    main()
