"""Schema and mathematical integrity tests for the Project Aurora sample dataset."""

import pytest


def test_config_json_schema(sample_config: dict):
    """Verify data/sample/config.json schema and 4 KPI pillars."""
    assert sample_config.get("project", {}).get("slug") == "sample"
    assert "name" in sample_config.get("project", {})
    assert "title" in sample_config.get("project", {})
    assert "features" in sample_config

    # Verify 4 KPI pillars
    assert "kpiPillars" in sample_config
    assert len(sample_config["kpiPillars"]) == 4


def test_risks_json_schema_and_math(sample_risks: list):
    """Verify 5x5 Likelihood x Consequence score math across all sample risks."""
    assert len(sample_risks) >= 25, "Sample risks dataset must have at least 25 records"

    for r in sample_risks:
        assert "id" in r
        assert "title" in r
        assert "status" in r

        # Verify 5x5 range
        inh_l = int(r.get("inherentLikelihood", 1))
        inh_c = int(r.get("inherentConsequence", 1))
        res_l = int(r.get("residualLikelihood", 1))
        res_c = int(r.get("residualConsequence", 1))

        assert 1 <= inh_l <= 5, f"Inherent likelihood out of range for {r.get('id')}"
        assert 1 <= inh_c <= 5, f"Inherent consequence out of range for {r.get('id')}"
        assert 1 <= res_l <= 5, f"Residual likelihood out of range for {r.get('id')}"
        assert 1 <= res_c <= 5, f"Residual consequence out of range for {r.get('id')}"

        assert int(r.get("inherentRiskScore")) == inh_l * inh_c
        assert int(r.get("residualRiskScore")) == res_l * res_c


def test_issues_json_schema(sample_issues: list):
    """Verify data/sample/issues.json records have required fields."""
    assert len(sample_issues) >= 10, "Sample issues dataset must have at least 10 records"
    for iss in sample_issues:
        assert "id" in iss
        assert "title" in iss
        assert "severity" in iss
        assert "status" in iss


def test_snapshots_json_schema(sample_snapshots: dict):
    """Verify data/sample/snapshots.json multi-week historical records and latest snapshot structure."""
    snapshots = sample_snapshots.get("snapshots", {})
    assert len(snapshots) >= 6, "Sample snapshots must have at least 6 historical weeks"

    # Verify latest snapshot structure
    latest = [s for s in snapshots.values() if s.get("isLatest") or s.get("isCurrent")]
    assert len(latest) >= 1
    latest_snap = latest[0]
    assert "synthesis" in latest_snap
    assert "top3" in latest_snap
    assert "sleeperOutlier" in latest_snap
    assert "podcastScript" in latest_snap


def test_driver_tree_and_knowledge_schema(sample_driver_tree: dict, sample_knowledge: dict):
    """Verify data/sample/driver_tree.json and knowledge.json solution blueprints."""
    assert sample_driver_tree is not None
    assert len(sample_knowledge.get("blueprints", [])) >= 8
