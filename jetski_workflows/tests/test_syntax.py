import pytest
import pathlib
import tomllib

def get_files(extensions):
    """Find all files with given extensions in the workspace relative to the workspace root."""
    # Assume this file is in tests/test_syntax.py, so parent.parent is the workspace root
    workspace_root = pathlib.Path(__file__).parent.parent
    files = []
    # Ignore git and temp dirs
    ignore_dirs = {'.git', '__temp_upstream__', '__pycache__', '.pytest_cache'}
    
    for path in workspace_root.rglob('*'):
        if path.is_file() and path.suffix in extensions:
            # Check if any part of the path is in ignore list
            if any(part in ignore_dirs for part in path.parts):
                continue
            files.append(path)
    return files

# Parameterize tests for each toml file
@pytest.mark.parametrize("toml_file", get_files(['.toml']))
def test_toml_syntax(toml_file):
    """Verify that a TOML file can be parsed successfully."""
    with open(toml_file, "rb") as f:
        try:
            tomllib.load(f)
        except Exception as e:
            pytest.fail(f"Failed to parse TOML {toml_file.name}: {e}")

# Parameterize tests for each md file
@pytest.mark.parametrize("md_file", get_files(['.md']))
def test_md_syntax(md_file):
    """Verify that a Markdown file is valid UTF-8 and non-empty."""
    with open(md_file, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            assert len(content) > 0, f"Markdown file {md_file.name} is empty"
        except UnicodeDecodeError as e:
            pytest.fail(f"Markdown file {md_file.name} contains invalid UTF-8: {e}")
