"""Unit tests for the spec drift detector agent skill."""

import json
import os
import tempfile
from typing import Any

try:
  from absl.testing import absltest
except ImportError:
  import unittest as absltest

try:
  from google3.net.slo.l3._agents.skills.spec_drift_detector.scripts import (
      drift_detector,
  )
except ImportError:
  try:
    from . import drift_detector
  except ImportError:
    import drift_detector



class DriftDetectorTest(absltest.TestCase):

  def test_match_path_exact(self):
    self.assertTrue(
        drift_detector._match_path("net/slo/l3/foo.cc", "net/slo/l3/foo.cc")
    )
    self.assertFalse(
        drift_detector._match_path("net/slo/l3/foo.cc", "net/slo/l3/bar.cc")
    )

  def test_match_path_prefix(self):
    self.assertTrue(
        drift_detector._match_path("net/slo/l3/", "net/slo/l3/foo.cc")
    )
    self.assertTrue(
        drift_detector._match_path("net/slo/l3/", "net/slo/l3/subdir/foo.cc")
    )
    self.assertFalse(
        drift_detector._match_path("net/slo/l3/", "net/slo/bar.cc")
    )

  def test_match_path_suffix(self):
    self.assertTrue(drift_detector._match_path("foo.cc", "net/slo/l3/foo.cc"))
    self.assertTrue(drift_detector._match_path("foo.cc", "foo.cc"))
    self.assertFalse(drift_detector._match_path("foo.cc", "net/slo/l3/bar.cc"))
    self.assertFalse(
        drift_detector._match_path("foo.cc", "net/slo/l3/foo.cc.old")
    )

  def test_match_path_glob(self):
    self.assertTrue(
        drift_detector._match_path("net/slo/*/*.cc", "net/slo/l3/foo.cc")
    )
    self.assertFalse(
        drift_detector._match_path("net/slo/*/*.cc", "net/slo/l3/foo.h")
    )

  def test_match_path_partial_suffix(self):
    self.assertTrue(
        drift_detector._match_path(
            "topology_reader/foo.cc", "net/slo/l3/topology_reader/foo.cc"
        )
    )
    self.assertTrue(
        drift_detector._match_path(
            "l3/topology_reader/foo.cc", "net/slo/l3/topology_reader/foo.cc"
        )
    )
    # Should not match if it's not a full path component suffix
    self.assertFalse(
        drift_detector._match_path(
            "reader/foo.cc", "net/slo/l3/topology_reader/foo.cc"
        )
    )
    # Exact match should still work
    self.assertTrue(
        drift_detector._match_path(
            "topology_reader/foo.cc", "topology_reader/foo.cc"
        )
    )


class DetectDriftTest(absltest.TestCase):

  def test_detect_drift_matches(self):
    mappings = [
        {"spec": "spec1", "files": ["net/slo/l3/foo.cc", "bar.cc"]},
        {"spec": "spec2", "files": ["baz/"]},
    ]
    modified_files = ["net/slo/l3/foo.cc", "baz/qux.cc", "other.cc"]
    results = drift_detector.detect_drift(modified_files, mappings)
    expected = [
        {"spec": "spec1", "matched_files": ["net/slo/l3/foo.cc"]},
        {"spec": "spec2", "matched_files": ["baz/qux.cc"]},
    ]
    self.assertEqual(results, expected)

  def test_detect_drift_no_matches(self):
    mappings = [
        {"spec": "spec1", "files": ["net/slo/l3/foo.cc"]},
    ]
    modified_files = ["bar.cc"]
    results = drift_detector.detect_drift(modified_files, mappings)
    self.assertEqual(results, [])


class DriftDetectorMainTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.test_dir = tempfile.TemporaryDirectory()
    self.config_path = os.path.join(self.test_dir.name, "config.json")

  def tearDown(self):
    self.test_dir.cleanup()
    super().tearDown()

  def write_config(self, content: Any) -> None:
    with open(self.config_path, "w") as config_file:
      json.dump(content, config_file)

  def call_main(
      self,
      modified_files: str = "net/slo/l3/foo.cc",
      config_path: str | None = None,
  ) -> None:
    """Calls drift_detector.main with specified arguments."""
    if config_path is None:
      config_path = self.config_path
    drift_detector.main([
        f"--modified_files={modified_files}",
        f"--config_path={config_path}",
    ])

  def test_main_success(self):
    self.write_config(
        {"mappings": [{"spec": "spec1", "files": ["net/slo/l3/foo.cc"]}]}
    )
    try:
      self.call_main()
    except SystemExit as err:
      self.fail(f"main raised SystemExit unexpectedly: {err}")

  def test_main_no_matches(self):
    self.write_config(
        {"mappings": [{"spec": "spec1", "files": ["net/slo/l3/foo.cc"]}]}
    )
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main(modified_files="net/slo/l3/bar.cc")
    self.assertEqual(exit_context.exception.code, 3)

  def test_main_config_not_found(self):
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main(config_path="non_existent_file.json")
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_invalid_json(self):
    with open(self.config_path, "w") as config_file:
      config_file.write("invalid json")
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_config_not_dict(self):
    self.write_config([{"mappings": []}])
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_config_missing_mappings(self):
    self.write_config({"invalid_key": []})
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_mappings_not_list(self):
    self.write_config({"mappings": "not a list"})
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_mapping_entry_not_dict(self):
    self.write_config({"mappings": ["not a dict"]})
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_mapping_entry_missing_spec(self):
    self.write_config({"mappings": [{"files": ["foo.cc"]}]})
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_mapping_entry_missing_files(self):
    self.write_config({"mappings": [{"spec": "spec1"}]})
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_mapping_entry_files_not_list(self):
    self.write_config({"mappings": [{"spec": "spec1", "files": "not a list"}]})
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main()
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_space_separated_files(self):
    self.write_config(
        {"mappings": [{"spec": "spec1", "files": ["net/slo/l3/foo.cc"]}]}
    )
    with self.assertRaises(SystemExit) as exit_context:
      self.call_main(modified_files="net/slo/l3/foo.cc net/slo/l3/bar.cc")
    self.assertEqual(exit_context.exception.code, 1)

  def test_main_comma_separated_with_spaces(self):
    self.write_config(
        {"mappings": [{"spec": "spec1", "files": ["net/slo/l3/foo.cc"]}]}
    )
    try:
      self.call_main(modified_files="net/slo/l3/foo.cc ,  net/slo/l3/bar.cc")
    except SystemExit as err:
      self.fail(f"main raised SystemExit unexpectedly: {err}")

  def test_parse_frontmatter_valid(self):
    spec_path = os.path.join(self.test_dir.name, "example_spec.md")
    with open(spec_path, "w") as f:
      f.write(
          "---\n"
          "name: test-spec\n"
          "description: Test spec description\n"
          "files:\n"
          "  - 'foo.cc'\n"
          "  - 'subdir/*.h'\n"
          "---\n"
          "# Heading\n"
      )
    frontmatter = drift_detector.parse_frontmatter(spec_path)
    self.assertIsNotNone(frontmatter)
    self.assertEqual(frontmatter.get("name"), "test-spec")
    self.assertEqual(frontmatter.get("files"), ["foo.cc", "subdir/*.h"])

  def test_parse_frontmatter_invalid(self):
    spec_path = os.path.join(self.test_dir.name, "invalid_spec.md")
    with open(spec_path, "w") as f:
      f.write("# No frontmatter\nJust markdown text.")
    frontmatter = drift_detector.parse_frontmatter(spec_path)
    self.assertIsNone(frontmatter)

  def test_scan_frontmatter_specs(self):
    spec_dir = os.path.join(self.test_dir.name, "my_package")
    os.makedirs(spec_dir, exist_ok=True)
    spec_path = os.path.join(spec_dir, "feature_spec.md")
    with open(spec_path, "w") as f:
      f.write(
          "---\n"
          "name: feature-spec\n"
          "files:\n"
          "  - '*.cc'\n"
          "---\n"
      )
    mod_file = os.path.join(spec_dir, "impl.cc")
    results = drift_detector.scan_frontmatter_specs([mod_file])
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0]["spec"], spec_path)
    self.assertEqual(results[0]["matched_files"], [mod_file])


if __name__ == "__main__":
  absltest.main()
