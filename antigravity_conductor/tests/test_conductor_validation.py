import pytest
import pathlib
import tomllib
import re

def get_workspace_root():
    return pathlib.Path(__file__).parent.parent

def camel_to_kebab(name):
    # Convert camelCase to kebab-case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

def test_command_to_workflow_mappings():
    """Verify that every command TOML file has a corresponding Markdown workflow file."""
    root = get_workspace_root()
    commands_dir = root / "commands"
    workflows_dir = root / "workflows"
    
    assert commands_dir.exists(), "commands/ directory is missing"
    assert workflows_dir.exists(), "workflows/ directory is missing"
    
    # Get all TOML files in commands/
    toml_files = list(commands_dir.glob("*.toml"))
    assert len(toml_files) > 0, "No command TOML files found in commands/"
    
    for toml_path in toml_files:
        stem = toml_path.stem
        kebab = camel_to_kebab(stem)
        expected_workflow_name = f"conductor-{kebab}.md"
        expected_workflow_path = workflows_dir / expected_workflow_name
        
        assert expected_workflow_path.exists(), (
            f"Command '{toml_path.name}' is missing its corresponding workflow file: "
            f"expected '{expected_workflow_name}' under workflows/."
        )

@pytest.mark.parametrize("toml_file", (get_workspace_root() / "commands").glob("*.toml"))
def test_command_structure(toml_file):
    """Verify that each command TOML follows the structural conventions of Conductor."""
    with open(toml_file, "rb") as f:
        data = tomllib.load(f)
        
    assert "description" in data, f"Command TOML {toml_file.name} is missing 'description'"
    assert "prompt" in data, f"Command TOML {toml_file.name} is missing 'prompt'"
    
    prompt_content = data["prompt"]
    assert isinstance(prompt_content, str), f"Command TOML {toml_file.name} 'prompt' is not a string"
    assert len(prompt_content.strip()) > 0, f"Command TOML {toml_file.name} 'prompt' is empty"
    
    # Check for standard Conductor section headers
    assert "## 1.0 SYSTEM DIRECTIVE" in prompt_content, (
        f"Command {toml_file.name} is missing '## 1.0 SYSTEM DIRECTIVE' header"
    )
    if toml_file.name != "setup.toml":
        assert "## 1.1 SETUP CHECK" in prompt_content, (
            f"Command {toml_file.name} is missing '## 1.1 SETUP CHECK' header"
        )

