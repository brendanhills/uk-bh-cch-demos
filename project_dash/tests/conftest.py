"""Shared pytest fixtures for Project Dash test suites.

Provides standardized fixtures for sample datasets, project configurations,
temporary isolated workspaces, and pipeline mocking.
"""

import json
import os
import shutil
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Returns the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def sample_project_dir(project_root: Path) -> Path:
    """Returns the Path to data/sample/ directory."""
    return project_root / "data" / "sample"


@pytest.fixture(scope="session")
def sample_dir(sample_project_dir: Path) -> Path:
    """Alias for sample_project_dir."""
    return sample_project_dir


@pytest.fixture(scope="session")
def sample_config(sample_project_dir: Path) -> dict:
    """Loads and returns data/sample/config.json."""
    config_path = sample_project_dir / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_risks(sample_project_dir: Path) -> list:
    """Loads and returns data/sample/risks.json."""
    risks_path = sample_project_dir / "risks.json"
    with open(risks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("risks", data) if isinstance(data, dict) else data


@pytest.fixture(scope="session")
def sample_issues(sample_project_dir: Path) -> list:
    """Loads and returns data/sample/issues.json."""
    issues_path = sample_project_dir / "issues.json"
    with open(issues_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("issues", data) if isinstance(data, dict) else data


@pytest.fixture(scope="session")
def sample_snapshots(sample_project_dir: Path) -> dict:
    """Loads and returns data/sample/snapshots.json."""
    snapshots_path = sample_project_dir / "snapshots.json"
    with open(snapshots_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_driver_tree(sample_project_dir: Path) -> dict:
    """Loads and returns data/sample/driver_tree.json."""
    driver_tree_path = sample_project_dir / "driver_tree.json"
    with open(driver_tree_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_knowledge(sample_project_dir: Path) -> dict:
    """Loads and returns data/sample/knowledge.json."""
    knowledge_path = sample_project_dir / "knowledge.json"
    with open(knowledge_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def tmp_project_workspace(tmp_path: Path, sample_project_dir: Path) -> Path:
    """Creates a temporary, isolated workspace directory pre-populated with sample project data.
    
    Returns the root path containing a sample/ subdirectory.
    """
    workspace = tmp_path / "data"
    workspace.mkdir(parents=True, exist_ok=True)
    target_sample = workspace / "sample"
    shutil.copytree(sample_project_dir, target_sample)
    return workspace


@pytest.fixture
def mock_pipeline_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Sets up an isolated pipeline environment with mock environment variables and data dir."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DEFAULT_PROJECT", "sample")
    monkeypatch.setenv("ENABLE_DRIVE_SCAN", "false")
    return data_dir
