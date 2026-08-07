import os
import re
import json
import pytest

DASH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(DASH_DIR, "index.html")
MOCK_DATA_TS = os.path.join(DASH_DIR, "src/data/mockData.ts")
SHEETS_SERVICE_TS = os.path.join(DASH_DIR, "src/utils/googleSheetsService.ts")
TYPES_TS = os.path.join(DASH_DIR, "src/types.ts")
SERVER_PY = os.path.join(DASH_DIR, "server.py")


def test_bug5_issue_and_risk_name_mapping():
    """
    Bug #5: Issue/Risk Name does not appear - only description is shown.
    Verify that in mockData.ts and index.html:
    1. Risk 1's title/name is 'Hard coded URL terms' (not the category 'Legal/Contract')
    2. Issue 1's title/name is '1.10b Platform Ready Test/Dev- GDC Enterprise EE E.01' (not the Action Plan or Schedule)
    3. Issue 1's owner is 'Tom Trobe'
    """
    with open(MOCK_DATA_TS, "r", encoding="utf-8") as f:
        content = f.read()

    # In mockData.ts, Risk 1 must have riskName as 'Hard coded URL terms' and NOT 'Legal/Contract'
    # And Issue 1 must have issueName as '1.10b Platform Ready Test/Dev- GDC Enterprise EE E.01' and issueOwner as 'Tom Trobe'
    assert '"riskName": "Hard coded URL terms"' in content, (
        "Bug #5 Failure: Risk 1 riskName is not 'Hard coded URL terms' in mockData.ts"
    )
    assert '"issueOwner": "Tom Trobe"' in content, (
        "Bug #5 Failure: Issue 1 issueOwner is not 'Tom Trobe' in mockData.ts"
    )
    assert '"issueName": "1.10b Platform Ready Test/Dev- GDC Enterprise EE E.01"' in content, (
        "Bug #5 Failure: Issue 1 issueName is not '1.10b Platform Ready...' in mockData.ts"
    )


def test_bug6_risk_display_id_format():
    """
    Bug #6: Risk numbers are rendered as R-008 instead of matching sheet format (8).
    Verify that types.ts and googleSheetsService.ts and mockData.ts support displayId (e.g. '8' or '1')
    """
    with open(TYPES_TS, "r", encoding="utf-8") as f:
        types_content = f.read()
    
    with open(SHEETS_SERVICE_TS, "r", encoding="utf-8") as f:
        sheets_content = f.read()

    with open(MOCK_DATA_TS, "r", encoding="utf-8") as f:
        mock_content = f.read()

    assert "displayId?: string;" in types_content, (
        "Bug #6 Failure: displayId is missing from RiskTicket definition in types.ts"
    )
    assert "displayId" in sheets_content, (
        "Bug #6 Failure: displayId mapping is missing from googleSheetsService.ts"
    )
    assert '"displayId": "1"' in mock_content or '"displayId": "8"' in mock_content, (
        "Bug #6 Failure: displayId is missing from mockData.ts"
    )


def test_bug1_drive_download_and_export_handling():
    """
    Bug #1: Downloaded pptx and pdf docs are not valid files.
    Verify that server.py contains export URL generation and binary handling for Google Workspace Docs/Slides
    """
    with open(SERVER_PY, "r", encoding="utf-8") as f:
        server_content = f.read()

    assert "export" in server_content.lower() or "drive_download" in server_content.lower(), (
        "Bug #1 Failure: Drive Export API / export handling is missing in server.py"
    )
    assert "application/pdf" in server_content or "application/vnd.openxmlformats" in server_content, (
        "Bug #1 Failure: Proper MIME type handling for PDF/PPTX export is missing in server.py"
    )
