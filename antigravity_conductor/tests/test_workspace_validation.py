import pytest
import pathlib
import json
import re

def get_workspace_root():
    return pathlib.Path(__file__).parent.parent

def find_active_workspaces():
    """Returns the current workspace root directory as the focus of local testing."""
    return [get_workspace_root()]

@pytest.mark.parametrize("workspace", find_active_workspaces())
def test_bugs_json_integrity(workspace):
    """Verify that any active .agents/bugs.json in workspaces contains valid and compliant bug objects."""
    bugs_file = workspace / ".agents" / "bugs.json"
    if not bugs_file.exists():
        pytest.skip(f"No bugs.json in {workspace.name}")
        
    with open(bugs_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Bugs JSON file {bugs_file} is not valid JSON: {e}")
            
    # Support both list format [...] and object-wrapped list format {"bugs": [...]}
    if isinstance(data, dict) and "bugs" in data:
        data = data["bugs"]
        
    assert isinstance(data, list), f"Bugs JSON {bugs_file} must parse to a list of bugs"
    
    # We support multiple date fields (date_reported or date) to be fully compatible with legacy formats
    valid_statuses = {"New", "Investigating", "Investigated", "Fix Implemented", "Fix Verified", "Closed"}
    valid_priorities = {"P0", "P1", "P2", "P3"}
    valid_impacts = {"Critical", "High", "Medium", "Low"}
    
    seen_ids = set()
    for bug in data:
        assert isinstance(bug, dict), f"Bug entry in {bugs_file.name} is not an object"
        
        # ID check
        assert "id" in bug, f"Bug entry in {bugs_file.name} is missing 'id'"
        bug_id = bug["id"]
        assert isinstance(bug_id, int), f"Bug ID must be an integer, got {type(bug_id)} in {bugs_file.name}"
        assert bug_id not in seen_ids, f"Duplicate bug ID {bug_id} found in {bugs_file.name}"
        seen_ids.add(bug_id)
        
        # Description check
        assert "description" in bug, f"Bug entry in {bugs_file.name} is missing 'description'"
        assert len(bug["description"].strip()) > 0, f"Empty description in bug #{bug_id}"
        
        # Status/Priority/Impact Checks (Optional checks, only validated if present in the entry)
        if "status" in bug:
            assert bug["status"] in valid_statuses, f"Invalid status '{bug['status']}' in bug #{bug_id}"
        if "priority" in bug:
            assert bug["priority"] in valid_priorities, f"Invalid priority '{bug['priority']}' in bug #{bug_id}"
        if "impact" in bug:
            assert bug["impact"] in valid_impacts, f"Invalid impact '{bug['impact']}' in bug #{bug_id}"

@pytest.mark.parametrize("workspace", find_active_workspaces())
def test_conductor_tracks_integrity(workspace):
    """Verify that conductor/tracks.md (if present) has valid links and all referenced folders exist."""
    tracks_file = workspace / "conductor" / "tracks.md"
    if not tracks_file.exists():
        pytest.skip(f"No tracks.md in {workspace.name}")
        
    with open(tracks_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract markdown links like [Track Name](tracks/some_folder) or similar
    links = re.findall(r'\[.*?\]\((.*?)\)', content)
    
    for link in links:
        # We only care about links pointing to tracks folder
        if "tracks/" in link:
            # Clean up query params or relative path indicators if any
            clean_link = link.split("#")[0].split("?")[0]
            # Strip leading './' if present to resolve path correctly
            clean_link = clean_link.lstrip("./")
            referenced_path = (workspace / "conductor" / clean_link).resolve()
            
            assert referenced_path.exists(), (
                f"Tracks registry {tracks_file} references a missing path: "
                f"'{clean_link}' does not exist relative to conductor/."
            )
            
            # If the link refers to a directory, ensure it contains key Conductor files
            if referenced_path.is_dir():
                spec = referenced_path / "spec.md"
                plan = referenced_path / "plan.md"
                metadata = referenced_path / "metadata.json"
                
                # A valid Conductor track should have at least some specifications or plan
                has_conforming_files = spec.exists() or plan.exists() or metadata.exists()
                assert has_conforming_files, (
                    f"Track folder '{referenced_path}' is empty or missing spec/plan/metadata."
                )
