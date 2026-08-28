"""Pass 1 of Spec Drift Detector.

Filters modified files against a configuration mapping spec files to code files
or auto-discovers specification markdown files via YAML frontmatter.

Exit codes:
  0: Modified files matched spec mappings.
  1: Error (e.g., config file not found or invalid JSON).
  3: No specs matched the modified files.
"""

import argparse
from collections.abc import Sequence
import fnmatch
import json
import os
import sys
from typing import Any


def _match_path(pattern: str, path: str) -> bool:
  """Checks if a path matches a pattern (prefix, suffix, glob, or exact)."""
  # Prefix match for directories
  if pattern.endswith('/'):
    return path.startswith(pattern)

  # Standard glob matching case-sensitively
  if fnmatch.fnmatchcase(path, pattern):
    return True

  # Suffix match (including partial paths)
  if path == pattern or path.endswith('/' + pattern):
    return True

  return False


def parse_frontmatter(file_path: str) -> dict[str, Any] | None:
  """Parses simple YAML-like frontmatter from a markdown file."""
  if not os.path.exists(file_path):
    return None

  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      content = f.read()
  except OSError as e:
    print(f'Failed to read {file_path}: {e}', file=sys.stderr)
    return None

  if not content.startswith('---\n') and not content.startswith('---\r\n'):
    return None

  parts = content.split('---', 2)
  if len(parts) < 3:
    return None

  frontmatter_text = parts[1]
  data: dict[str, Any] = {}
  current_key = None
  for line in frontmatter_text.splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
      continue

    if line.startswith('-'):
      val = line[1:].strip().strip('"').strip("'")
      if current_key and isinstance(data.get(current_key), list):
        data[current_key].append(val)
      continue

    if ':' in line:
      key, val = line.split(':', 1)
      current_key = key.strip()
      val = val.strip().strip('"').strip("'")
      if not val:
        data[current_key] = []
      else:
        data[current_key] = val

  return data


def scan_frontmatter_specs(
    modified_files: Sequence[str],
) -> list[dict[str, Any]]:
  """Discovers spec markdown files with YAML frontmatter for modified files."""
  spec_matches: dict[str, list[str]] = {}

  for m_file in modified_files:
    current_dir = os.path.dirname(m_file)
    if not current_dir:
      current_dir = '.'

    visited_dirs: set[str] = set()
    while True:
      if not os.path.exists(current_dir) or current_dir in visited_dirs:
        break
      visited_dirs.add(current_dir)

      try:
        files_in_dir = os.listdir(current_dir)
      except OSError as e:
        print(f'Failed to list directory {current_dir}: {e}', file=sys.stderr)
        break

      spec_files = [
          os.path.join(current_dir, f)
          for f in files_in_dir
          if f.lower().endswith('spec.md')
          and os.path.isfile(os.path.join(current_dir, f))
      ]

      for spec_path in spec_files:
        frontmatter = parse_frontmatter(spec_path)
        if not frontmatter:
          continue

        patterns = frontmatter.get('files', [])
        if not isinstance(patterns, list):
          continue

        spec_dir = os.path.dirname(spec_path)
        rel_path = os.path.relpath(m_file, spec_dir)
        basename = os.path.basename(m_file)

        for pattern in patterns:
          if (
              _match_path(pattern, rel_path)
              or _match_path(pattern, basename)
              or _match_path(pattern, m_file)
          ):
            if spec_path not in spec_matches:
              spec_matches[spec_path] = []
            if m_file not in spec_matches[spec_path]:
              spec_matches[spec_path].append(m_file)
            break

      parent_dir = os.path.dirname(current_dir)
      if (
          not parent_dir
          or parent_dir == current_dir
          or current_dir in ('.', '/')
      ):
        break
      current_dir = parent_dir

  return [
      {'spec': spec, 'matched_files': files}
      for spec, files in spec_matches.items()
  ]


def detect_drift(
    modified_files: Sequence[str],
    mappings: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
  """Filters modified files against spec config mappings."""
  drift_results = []
  for mapping in mappings:
    spec = mapping.get('spec')
    patterns = mapping.get('files', [])

    matched_files = [
        modified_file
        for modified_file in modified_files
        if any(_match_path(pattern, modified_file) for pattern in patterns)
    ]

    if matched_files:
      drift_results.append({'spec': spec, 'matched_files': matched_files})
  return drift_results


def main(args: Sequence[str] | None = None) -> None:
  """Parses arguments and runs the drift detection.

  Args:
    args: Command-line arguments. If None, sys.argv[1:] is used.

  Returns:
    None.
  """
  parser = argparse.ArgumentParser(description='Spec Drift Detector')
  parser.add_argument(
      '--modified_files',
      required=True,
      help='Comma-separated list of modified files (relative to google3).',
  )
  parser.add_argument(
      '--config_path',
      required=False,
      default=None,
      help='Path to the spec mappings JSON config file.',
  )
  parser.add_argument(
      '--scan_specs',
      action='store_true',
      default=False,
      help='Scan parent directories for *spec.md files with YAML frontmatter.',
  )
  parsed_args = parser.parse_args(args)

  mappings = []
  if parsed_args.config_path:
    try:
      with open(parsed_args.config_path, 'r') as config_file:
        config = json.load(config_file)
    except FileNotFoundError:
      print(
          f'Config file not found: {parsed_args.config_path}', file=sys.stderr
      )
      sys.exit(1)
    except (OSError, json.JSONDecodeError) as err:
      print(f'Failed to load config: {err}', file=sys.stderr)
      sys.exit(1)

    try:
      if not isinstance(config, dict):
        raise ValueError('Config root must be a JSON object')

      mappings_list = config.get('mappings')
      if mappings_list is None:
        raise ValueError("Config missing 'mappings' key")
      if not isinstance(mappings_list, list):
        raise ValueError("'mappings' must be a list")

      for i, mapping in enumerate(mappings_list):
        if not isinstance(mapping, dict):
          raise ValueError(f'Mapping entry {i} must be a JSON object')
        if 'spec' not in mapping:
          raise ValueError(f"Mapping entry {i} missing 'spec' key")
        if 'files' not in mapping:
          raise ValueError(f"Mapping entry {i} missing 'files' key")
        if not isinstance(mapping['files'], list):
          raise ValueError(f"Mapping entry {i} 'files' must be a list")
      mappings = mappings_list
    except (TypeError, ValueError, AttributeError) as err:
      print(f'Invalid config schema: {err}', file=sys.stderr)
      sys.exit(1)

  modified_files = [
      file_path.strip()
      for file_path in parsed_args.modified_files.split(',')
      if file_path.strip()
  ]

  for file_path in modified_files:
    if ' ' in file_path:
      print(
          f"Error: Invalid file path '{file_path}'. The --modified_files list "
          'must be comma-separated, not space-separated.',
          file=sys.stderr,
      )
      sys.exit(1)

  drift_results: list[dict[str, Any]] = []
  if mappings:
    drift_results.extend(detect_drift(modified_files, mappings))

  if parsed_args.scan_specs or not parsed_args.config_path:
    frontmatter_results = scan_frontmatter_specs(modified_files)
    existing_specs = {r['spec'] for r in drift_results}
    for fr in frontmatter_results:
      if fr['spec'] not in existing_specs:
        drift_results.append(fr)

  print(json.dumps(drift_results, indent=2))
  if not drift_results:
    sys.exit(3)


if __name__ == '__main__':
  main(sys.argv[1:])
