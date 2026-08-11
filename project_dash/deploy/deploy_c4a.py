#!/usr/bin/env python3
"""
F-DSE Risk Intelligence Platform — C4A Starter Deployment Script
Syncs local frontend assets (index.html, assets/) to GitHub Enterprise,
pushes an update branch, and provides a 1-click Pull Request link
to trigger automated Cloud Run rollout.
"""

import argparse
import datetime
import os
import pathlib
import shutil
import subprocess
import sys

REPO_SSH = "git@depot.code.corp.goog:ai-studio-prototypes-exp/f-dse-risk-intelligence-dashboard.git"
REPO_HTTPS = "https://depot.code.corp.goog/ai-studio-prototypes-exp/f-dse-risk-intelligence-dashboard.git"
REPO_WEB = "https://depot.code.corp.goog/ai-studio-prototypes-exp/f-dse-risk-intelligence-dashboard"
CLOUD_RUN_URL = "https://f-dse-risk-intelligence-dashboard-1032469575739.us-central1.run.app"
C4A_APP_URL = "https://start.c4a.corp.goog/applications?focus=5096694286909440"

DEPLOY_FOLDER = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = DEPLOY_FOLDER.parent
REPO_DIR = DEPLOY_FOLDER / ".repo"


def run_cmd(cmd, cwd=None, capture=False, check=True):
    """Run a shell command and handle errors gracefully."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
        check=False
    )
    if check and result.returncode != 0:
        err = result.stderr.strip() if result.stderr else "Command failed"
        print(f"\n❌ Error running {' '.join(cmd)}: {err}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def ensure_repo_cloned():
    """Ensure the GitHub Enterprise repository is cloned into deploy/.repo."""
    if REPO_DIR.exists() and (REPO_DIR / ".git").exists():
        print("📦 Using cached deployment repository at deploy/.repo")
        return

    print("📥 Cloning GitHub Enterprise repository for C4A...")
    REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
    
    # Try SSH first, fallback to HTTPS if SSH key isn't set up yet
    res = run_cmd(["git", "clone", REPO_SSH, str(REPO_DIR)], check=False)
    if res.returncode != 0:
        print("ℹ️ SSH clone failed, attempting HTTPS clone...")
        run_cmd(["git", "clone", REPO_HTTPS, str(REPO_DIR)], check=True)


def sync_files():
    """Sync index.html and assets/ to the deployment repository."""
    # 1. Sync index.html
    src_html = PROJECT_ROOT / "index.html"
    dest_html = REPO_DIR / "index.html"
    shutil.copy2(src_html, dest_html)

    # 2. Sync assets/ directory (excluding .aistudio and hidden files)
    src_assets = PROJECT_ROOT / "assets"
    dest_assets = REPO_DIR / "assets"
    if src_assets.exists():
        if dest_assets.exists():
            shutil.rmtree(dest_assets)
        shutil.copytree(
            src_assets,
            dest_assets,
            ignore=shutil.ignore_patterns(".*", ".aistudio*")
        )


def main():
    parser = argparse.ArgumentParser(
        description="Deploy F-DSE Dashboard updates to C4A Starter (Cloud Run)."
    )
    parser.add_argument(
        "-m", "--message",
        type=str,
        default="",
        help="Custom commit message describing the update"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without committing or pushing"
    )

    args = parser.parse_args()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"deploy-{timestamp}"
    commit_msg = args.message or f"Update dashboard - {timestamp}"

    print("=" * 64)
    print("🚀 F-DSE Risk Intelligence Platform — C4A Deployment Pipeline")
    print("=" * 64)

    ensure_repo_cloned()

    # Step 1: Prepare clean main branch
    print("🔄 Updating repository from main...")
    run_cmd(["git", "checkout", "main"], cwd=REPO_DIR)
    run_cmd(["git", "pull", "--rebase", "origin", "main"], cwd=REPO_DIR, check=False)

    # Step 2: Create new deployment branch
    print(f"🌿 Creating branch '{branch_name}'...")
    run_cmd(["git", "checkout", "-b", branch_name], cwd=REPO_DIR)

    # Step 3: Copy latest files
    print("📂 Syncing latest index.html and assets...")
    sync_files()

    # Step 4: Check diff
    status_res = run_cmd(["git", "status", "--porcelain"], cwd=REPO_DIR, capture=True)
    changes = status_res.stdout.strip()

    if not changes:
        print("\n✅ No changes detected between local files and remote main.")
        print(f"🌐 Live Cloud Run URL: {CLOUD_RUN_URL}")
        return

    print("\n📝 Pending changes to deploy:")
    for line in changes.splitlines():
        print(f"   {line}")

    if args.dry_run:
        print("\n🔍 Dry-run mode active. No changes were committed or pushed.")
        return

    # Step 5: Commit and Push
    print(f"\n💾 Committing: '{commit_msg}'...")
    run_cmd(["git", "add", "."], cwd=REPO_DIR)
    run_cmd(["git", "commit", "-m", commit_msg], cwd=REPO_DIR)

    print(f"⬆️ Pushing branch '{branch_name}' to GitHub Enterprise...")
    run_cmd(["git", "push", "-u", "origin", branch_name], cwd=REPO_DIR)

    # Step 6: Output summary
    pr_url = f"{REPO_WEB}/pull/new/{branch_name}"

    print("\n" + "=" * 64)
    print("🎉 DEPLOYMENT BRANCH PUSHED SUCCESSFULLY!")
    print("=" * 64)
    print(f"  👉 1-Click Pull Request:  {pr_url}")
    print(f"  🌐 Live Cloud Run URL:    {CLOUD_RUN_URL}")
    print(f"  📊 C4A App Dashboard:    {C4A_APP_URL}")
    print("=" * 64)
    print("\n📌 Next Step:")
    print("   Open the 1-Click Pull Request link above and click 'Merge Pull Request'.")
    print("   GitHub Actions will automatically build and deploy your update to Cloud Run!\n")


if __name__ == "__main__":
    main()
