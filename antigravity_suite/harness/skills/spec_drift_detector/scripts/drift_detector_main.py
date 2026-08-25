"""Thin entrypoint for drift_detector."""

import sys

from google3.net.slo.l3._agents.skills.spec_drift_detector.scripts import (
    drift_detector,
)


def main() -> None:
  drift_detector.main(sys.argv[1:])


if __name__ == '__main__':
  main()
