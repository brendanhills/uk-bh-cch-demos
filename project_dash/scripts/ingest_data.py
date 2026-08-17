import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

DATA_BASE_DIR = os.path.join(BASE_DIR, 'data')

from scripts.precompute_analytics import build_precomputed_analytics
from scripts.gemini_generator import generate_executive_synthesis, generate_multispeaker_podcast, get_gemini_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('ingest_data')

def resolve_target_projects(cli_arg: Optional[str] = None) -> List[str]:
    """Resolves target projects from CLI flag or .env configuration."""
    if cli_arg:
        return [cli_arg.strip()]
    
    env_projects = os.getenv('DEFAULT_PROJECTS') or os.getenv('PROJECTS') or os.getenv('ACTIVE_PROJECT')
    if env_projects:
        projects = [p.strip() for p in env_projects.split(',') if p.strip()]
        if projects:
            return projects

    return ['sample']

def get_project_dir(project_name: str) -> str:
    proj_dir = os.path.join(DATA_BASE_DIR, project_name)
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

def load_project_config(project_name: str) -> Dict[str, Any]:
    proj_dir = get_project_dir(project_name)
    config_file = os.path.join(proj_dir, 'config.json')
    
    default_config = {
        "project": {
            "slug": project_name,
            "name": project_name.replace('-', ' ').title(),
            "title": "Delivery Governance Dashboard",
            "organization": "Leadership Board"
        },
        "sources": {
            "googleSheets": {"enabled": False},
            "googleDrive": {"enabled": False},
            "geminiNotebooks": {"enabled": False}
        },
        "features": {
            "secondaryRegister": {"enabled": True},
            "audioBriefing": {"enabled": True},
            "driverTree": {"enabled": True},
            "knowledgeBase": {"enabled": True},
            "trends": {"enabled": True},
            "ledger": {"enabled": True}
        }
    }
    
    if os.path.exists(config_file):
        loaded = load_json_file(config_file, default_config)
        return loaded
    return default_config

def ingest_single_project(
    project_name: str,
    generate_ai: bool = False,
    model: str = 'gemini-3.5-flash'
) -> Dict[str, Any]:
    """Runs the complete multi-stream ingestion & precomputation pipeline for a single project."""
    proj_dir = get_project_dir(project_name)
    logger.info(f"=== Starting Ingestion Pipeline for Project: '{project_name}' ===")
    logger.info(f"Directory: {proj_dir}")

    config = load_project_config(project_name)
    sources = config.get('sources', {})

    # 1. Sync external streams if enabled
    if sources.get('googleSheets', {}).get('enabled'):
        logger.info(f"[Google Sheets Sync] Ingesting sheet: {sources['googleSheets'].get('sheetUrl', 'N/A')}")
        # Ingestion logic hooks can be triggered here

    if sources.get('googleDrive', {}).get('enabled'):
        logger.info(f"[Google Drive Sync] Ingesting Drive folder: {sources['googleDrive'].get('folderId', 'N/A')}")

    if sources.get('geminiNotebooks', {}).get('enabled'):
        logger.info(f"[Gemini Notebook Sync] Ingesting {len(sources['geminiNotebooks'].get('notebookIds', []))} notebooks")

    # 2. Load domain datasets
    risks_raw = load_json_file(os.path.join(proj_dir, 'risks.json'), [])
    risks = risks_raw.get('risks', risks_raw) if isinstance(risks_raw, dict) else risks_raw

    issues_raw = load_json_file(os.path.join(proj_dir, 'issues.json'), [])
    issues = issues_raw.get('issues', issues_raw) if isinstance(issues_raw, dict) else issues_raw

    snapshots_raw = load_json_file(os.path.join(proj_dir, 'snapshots.json'), {'snapshots': {}})
    snapshots = snapshots_raw.get('snapshots', {}) if isinstance(snapshots_raw, dict) else {}

    knowledge = load_json_file(os.path.join(proj_dir, 'knowledge.json'), {'blueprints': []})
    driver_tree = load_json_file(os.path.join(proj_dir, 'driver_tree.json'), {})

    # 3. Optional Gemini AI Briefing Generation for Latest Snapshot
    if generate_ai and snapshots:
        sorted_weeks = sorted(snapshots.values(), key=lambda x: x.get('weekNumber', 0))
        latest_snap = sorted_weeks[-1] if sorted_weeks else None
        if latest_snap:
            logger.info(f"[Gemini AI] Generating executive briefing for {latest_snap.get('weekLabel', 'Latest Week')} using {model}...")
            metric_ctx = {
                'project_name': config.get('project', {}).get('name', project_name),
                'project_title': config.get('project', {}).get('title', ''),
                'organization': config.get('project', {}).get('organization', ''),
                'report_week': latest_snap.get('weekLabel', 'Current Week'),
                'report_date': latest_snap.get('date', ''),
                'overall_status': latest_snap.get('overallStatus', 'AMBER (Stable)'),
                'total_risks': len(risks),
                'total_issues': len(issues)
            }
            try:
                synthesis_result = generate_executive_synthesis(metric_ctx, latest_snap.get('plans', []), model=model)
                podcast_script = generate_multispeaker_podcast(metric_ctx, synthesis_result, model=model)
                latest_snap['synthesis'] = synthesis_result.get('synthesis', {})
                latest_snap['top3'] = synthesis_result.get('top3', [])
                latest_snap['sleeperOutlier'] = synthesis_result.get('sleeperOutlier', {})
                latest_snap['podcastScript'] = podcast_script
                latest_snap['generatedBy'] = model
                save_json_file(os.path.join(proj_dir, 'snapshots.json'), {'snapshots': snapshots})
                logger.info("[Gemini AI] AI synthesis successfully updated.")
            except Exception as e:
                logger.warning(f"[Gemini AI] Skipped AI synthesis due to error: {e}")

    # 4. Run Pre-Computation Analytics Engine
    logger.info("[Pre-Computation] Building analytical caches (5x5 matrices, burndown, blueprint mappings)...")
    analytics = build_precomputed_analytics(risks, issues, snapshots, knowledge, driver_tree)
    analytics_file = os.path.join(proj_dir, 'precomputed_analytics.json')
    save_json_file(analytics_file, analytics)
    logger.info(f"[Pre-Computation] Saved precomputed cache to {analytics_file}")

    return {
        "success": True,
        "project": project_name,
        "totalRisks": len(risks),
        "totalIssues": len(issues),
        "totalSnapshots": len(snapshots),
        "precomputedAnalyticsFile": analytics_file
    }

def main():
    parser = argparse.ArgumentParser(description="Master Data Ingestion & Pre-Computation Orchestrator")
    parser.add_argument('--project', help="Target project slug (e.g. 'sample', 'f-dse'). Defaults to DEFAULT_PROJECTS from .env")
    parser.add_argument('--model', default=os.getenv('GEMINI_MODEL', 'gemini-3.5-flash'), help="Gemini model version")
    parser.add_argument('--ai', dest='generate_ai', action='store_true', help="Enable Gemini 3.5 AI briefing generation")
    parser.add_argument('--no-ai', dest='generate_ai', action='store_false', help="Disable Gemini AI generation")
    parser.set_defaults(generate_ai=False)
    args = parser.parse_args()

    target_projects = resolve_target_projects(args.project)
    logger.info(f"Target projects to ingest: {target_projects}")

    results = []
    for proj in target_projects:
        try:
            res = ingest_single_project(proj, generate_ai=args.generate_ai, model=args.model)
            results.append(res)
        except Exception as e:
            logger.error(f"Failed ingestion for project '{proj}': {e}", exc_info=True)
            results.append({"success": False, "project": proj, "error": str(e)})

    logger.info("=== Ingestion Orchestration Summary ===")
    for r in results:
        status_icon = "✓" if r.get('success') else "✗"
        logger.info(f"{status_icon} Project '{r['project']}': Success={r.get('success')}, Risks={r.get('totalRisks', 0)}, Issues={r.get('totalIssues', 0)}")

if __name__ == '__main__':
    main()
