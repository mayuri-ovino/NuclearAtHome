#!/usr/bin/env bash
# Run the Nuclear@Home test suite from the project root.
# Uses pytest if installed, otherwise Python's built-in unittest.
set -euo pipefail

cd "$(dirname "$0")/.."

if python3 -c "import pytest" >/dev/null 2>&1; then
    python3 -m pytest -q tests
else
    python3 -m unittest discover -s tests -t . -v
fi
