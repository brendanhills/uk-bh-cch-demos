import os
import sys
import json
import argparse
import re
from datetime import datetime

DATA_FILE = "/usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash/src/data/weekly_snapshots.json"

def load_snapshots():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"lastSynced": None, "driveFolderId": "1JIsbi35mXn4W-NxjbLTWo22FQMv_zv-C", "snapshots": {}}

def save_snapshots(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully updated snapshots in {DATA_FILE}")

def ingest_file(file_id, file_name, week_number=None, report_date=None):
    data = load_snapshots()
    
    # Infer week number and date if not provided
    if not week_number:
        m = re.search(r'Week\s*(\d+)', file_name, re.IGNORECASE)
        week_number = int(m.group(1)) if m else (max([s.get('weekNumber', 0) for s in data['snapshots'].values()] or [26]) + 1)

    if not report_date:
        m = re.search(r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})', file_name)
        report_date = m.group(1) if m else datetime.now().strftime("%d %b %Y")

    week_key = f"w{week_number}"
    week_label = f"Week {week_number}"

    print(f"Ingesting {file_name} as {week_label} ({report_date})...")

    # Mark all previous snapshots as not latest
    for k, v in data['snapshots'].items():
        v['isLatest'] = False

    # Create new week snapshot entry
    new_snapshot = {
        "weekNumber": week_number,
        "weekLabel": week_label,
        "date": report_date,
        "isLatest": True,
        "driveFileId": file_id,
        "driveFileName": file_name,
        "overallStatus": "🟡 AMBER (Stable)",
        "kpis": {
            "commercial": "🟢 ON TRACK",
            "ibr": "🟡 DUE AUG 2026 (90%)",
            "ato": "🟢 GREEN",
            "escalations": "🔴 5 ITEMS"
        },
        "plans": [
            {
                "num": 1,
                "status": "RED",
                "ref": "1.2b",
                "title": "Milestone 1 Deliverables Cth Acceptance",
                "plan": "GAP closure report created to work with the Cth for acceptance of milestone 1 deliverables.",
                "owner": "COL Tim Minion / Adam Flint",
                "target": "Aug 2026",
                "deltaNote": "Continuing Cth review of SRP, V&V, and IMS deliverable acceptance."
            },
            {
                "num": 2,
                "status": "RED",
                "ref": "1.6 GFF",
                "title": "E.01/E.02 Facilities & Connectivity",
                "plan": "Validating schedule impacts and mitigating delivery approach whilst connectivity is established.",
                "owner": "Aron Ward / Team Google",
                "target": "Aug 2026",
                "deltaNote": "Facility connectivity lead time under active mitigation."
            },
            {
                "num": 3,
                "status": "BLUE",
                "ref": "1.10b (I-129)",
                "title": "I-129 Delivered • GDC EE E.01 Test/Dev Ready",
                "plan": "Platform successfully validated and environment build commenced, with early release provided to initial systems.",
                "owner": "Tom Trobe / Daryl James",
                "target": "Delivered / Monitoring",
                "deltaNote": "Early release operational for test/dev systems."
            },
            {
                "num": 4,
                "status": "RED",
                "ref": "1.14",
                "title": "Systems Requirements Review (SRR) Glide Path",
                "plan": "Iterative approach to prioritise System Requirements for CD1.5, development of glide path similar to IBR.",
                "owner": "Scott Deacon / Dan Wurzer",
                "target": "Sep 2026",
                "deltaNote": "Prioritization glide path progressing."
            },
            {
                "num": 5,
                "status": "RED",
                "ref": "3.1",
                "title": "Application Discovery Report (ADR) Gap Closure",
                "plan": "Address in the Apps Focus Groups, direct engagement with System Owners.",
                "owner": "Steve Peel / Team Google",
                "target": "Aug 2026",
                "deltaNote": "Apps Focus Groups underway."
            }
        ]
    }

    data['snapshots'][week_key] = new_snapshot
    data['lastSynced'] = datetime.now().isoformat()
    save_snapshots(data)
    return new_snapshot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest weekly reporting pack")
    parser.add_argument("--file-id", default="dummy-id-w27", help="Google Drive file ID")
    parser.add_argument("--name", default="Weekly Reporting - Week 27 - 07 Aug 2026.pdf", help="Report file name")
    parser.add_argument("--week", type=int, help="Week number")
    parser.add_argument("--date", help="Report date")
    args = parser.parse_args()

    ingest_file(args.file_id, args.name, args.week, args.date)
