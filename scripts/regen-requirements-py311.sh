#!/usr/bin/env bash
set -euo pipefail

# Regenerate pinned requirements for Python 3.11
# Usage: scripts/regen-requirements-py311.sh [python-executable]
# Example: scripts/regen-requirements-py311.sh python3.11

PYTHON_CMD="${1:-}"
if [ -z "$PYTHON_CMD" ]; then
  if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_CMD=python3.11
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python3
  else
    echo "No python3.11 or python3 found; pass the python executable as first arg." >&2
    exit 1
  fi
fi

echo "Using Python: $(command -v $PYTHON_CMD)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR=".venv-py311"
echo "Creating virtualenv at $VENV_DIR"
$PYTHON_CMD -m venv "$VENV_DIR"
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install pip-tools

INFILE="requirements.in"
OUTFILE="requirements-py311.txt"

echo "Generating $INFILE from requirements.txt (stripping pins to isolate top-level packages)"
python - <<'PY' > "$INFILE"
import re

def top_level(req_line):
  # remove inline comments
  req_line = req_line.split('#', 1)[0].strip()
  if not req_line:
    return None
  # split on common version/operator separators or direct URL '@'
  parts = re.split(r"\s*(?:==|>=|<=|~=|!=|===|>|<|@)\s*", req_line, maxsplit=1)
  return parts[0].strip()

with open('requirements.txt', 'r', encoding='utf-8') as fh:
  for ln in fh:
    tl = top_level(ln)
    if tl:
      print(tl)
PY

echo "Running pip-compile to resolve compatible pins for Python 3.11"
pip-compile --output-file "$OUTFILE" --upgrade "$INFILE"

echo "New pinned requirements written to $OUTFILE"
echo "To install into the venv now run:"
echo "  source $VENV_DIR/bin/activate && python -m pip install -r $OUTFILE"

echo "If the results look good you may replace requirements.txt with $OUTFILE after review."
