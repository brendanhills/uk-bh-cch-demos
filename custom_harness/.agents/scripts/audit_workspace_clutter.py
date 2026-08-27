#!/usr/bin/env python3
"""
Workspace Clutter Auditor CLI
Audits a repository workspace for legacy, redundant, and unreferenced files,
calculates reduction metrics, and generates a structured archival plan.
"""

import os
import sys
import json
import argparse
import subprocess
from collections import defaultdict
from typing import Dict, List, Set, Any

IGNORED_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__",
    ".pytest_cache", ".idea", ".vscode", "archive"
}

def scan_workspace(root_dir: str) -> Dict[str, List[str]]:
    """Scan all files in the workspace grouped by top-level directory."""
    files_by_dir = defaultdict(list)
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".venv")]
        for f in files:
            if f.endswith(".pyc"):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, root_dir)
            top = rel_path.split(os.sep)[0] if os.sep in rel_path else "root"
            files_by_dir[top].append(rel_path)
    return dict(files_by_dir)

def get_git_tracked_files(root_dir: str) -> Set[str]:
    """Get list of all git-tracked files in the workspace."""
    try:
        res = subprocess.run(
            ["git", "ls-files"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return set(res.stdout.strip().splitlines())
    except Exception:
        return set()

def find_file_references(root_dir: str, target_name: str, target_base: str) -> List[str]:
    """Search for occurrences of a filename in specs, tests, bugs, and source files."""
    references = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".venv")]
        for f in files:
            p = os.path.normpath(os.path.join(root, f))
            rel = os.path.relpath(p, root_dir)
            if rel == target_name or rel.endswith(".pyc") or "archive" in rel:
                continue
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fl:
                    content = fl.read()
                    if target_name in content or (target_base in content and target_base not in ["README.md", "index.html", "config.json"]):
                        references.append(rel)
            except Exception:
                pass
    return references

def audit_clutter(root_dir: str) -> Dict[str, Any]:
    """Perform a comprehensive clutter audit on the target repository."""
    abs_root = os.path.abspath(root_dir)
    files_by_dir = scan_workspace(abs_root)
    tracked_files = get_git_tracked_files(abs_root)

    total_files = sum(len(flist) for flist in files_by_dir.values())

    candidate_files = []
    for top, flist in files_by_dir.items():
        for rel in flist:
            base = os.path.basename(rel)
            # Heuristic detection for candidates:
            is_candidate = False
            reason = ""

            if rel.startswith("src/components/") or rel.endswith(".tsx") or rel.endswith(".ts"):
                if not os.path.exists(os.path.join(abs_root, "package.json")) and not os.path.exists(os.path.join(abs_root, "tsconfig.json")):
                    is_candidate = True
                    reason = "Unused TypeScript/React prototype file without active package.json build"
            elif rel.startswith("scripts/") and base in ["ingest_data.py", "ingest_weekly_report.py", "sync_notebook.py"]:
                is_candidate = True
                reason = "Superseded script consolidated into pipeline.py"
            elif rel.startswith("deploy/") and base in ["deploy_gcp.sh", "shutdown.sh", "stop.sh", "nginx.conf"]:
                is_candidate = True
                reason = "Legacy VM/Nginx process script superseded by Cloud Run CI/CD"
            elif rel.startswith("data/notebook/") or "contracts_mapping" in base or "contracts_catalog" in base:
                is_candidate = True
                reason = "Deprecated notebook catalog/mapping artifact"
            elif rel.endswith(".zip") or base in ["package_zip.sh", "legacy_bundle.js"]:
                is_candidate = True
                reason = "Stale build package / monolithic bundle"

            if is_candidate:
                refs = find_file_references(abs_root, rel, base)
                candidate_files.append({
                    "file": rel,
                    "reason": reason,
                    "is_tracked": rel in tracked_files,
                    "reference_count": len(refs),
                    "references": refs[:5]
                })

    return {
        "workspace": abs_root,
        "total_files": total_files,
        "files_by_directory": {k: len(v) for k, v in files_by_dir.items()},
        "candidate_count": len(candidate_files),
        "potential_reduction_pct": round((len(candidate_files) / max(total_files, 1)) * 100, 1),
        "candidates": candidate_files
    }

def print_audit_report(report: Dict[str, Any]):
    print("=" * 80)
    print(f"📊 Workspace Clutter Audit Report: {report['workspace']}")
    print("=" * 80)
    print(f"Total Workspace Files (excluding venv/git): {report['total_files']}")
    print(f"Candidate Legacy / Redundant Files       : {report['candidate_count']}")
    print(f"Potential Codebase Clutter Reduction     : {report['potential_reduction_pct']}%\n")

    print("📁 File Counts by Directory:")
    print("-" * 50)
    for d, count in sorted(report["files_by_directory"].items()):
        print(f"  • {d:15s}: {count:3d} files")

    if report["candidates"]:
        print("\n📦 Identified Legacy & Candidate Files to Archive:")
        print("-" * 80)
        for cand in report["candidates"]:
            tracked_str = "Git Tracked" if cand["is_tracked"] else "Untracked"
            ref_str = f"{cand['reference_count']} refs" if cand['reference_count'] > 0 else "0 refs (Clean)"
            print(f"  • [{tracked_str}] {cand['file']}")
            print(f"    Reason: {cand['reason']} | Status: {ref_str}")
    else:
        print("\n✨ Workspace is lean and clean! No candidate legacy files detected.")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Audit workspace for legacy and redundant files.")
    parser.add_argument("path", nargs="?", default=".", help="Target workspace path (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON format")
    args = parser.parse_args()

    report = audit_clutter(args.path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_audit_report(report)

if __name__ == "__main__":
    main()
