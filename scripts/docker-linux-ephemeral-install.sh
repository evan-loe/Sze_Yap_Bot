#!/usr/bin/env bash
# This script is meant to make it easy to prepare the repository inside an
# ephemeral docker container (for example on TrueNAS). It will:
# - create a persistent data directory (default: /mnt/data/szeyap-bot-files)
# - create a Python virtual environment inside that data dir
# - install Python requirements from requirements.txt

set -euo pipefail

# Default persistent data directory (can be overridden via env var or first arg)
DATA_DIR="${1:-${DATA_DIR:-/mnt/data/szeyap-bot-files}}"

# Resolve script and repo paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Repository root: $REPO_ROOT"
echo "Persistent data directory: $DATA_DIR"

# Create data directory if missing
mkdir -p "$DATA_DIR"
echo "Created (or verified) $DATA_DIR"

# Ensure we have python3 available; try to install minimal runtime if missing
if ! command -v python3 >/dev/null 2>&1; then
	echo "python3 not found. Attempting to install system packages (apt or yum)."
	if command -v apt-get >/dev/null 2>&1; then
		apt-get update && apt-get install -y --no-install-recommends python3 python3-venv python3-distutils build-essential
	elif command -v yum >/dev/null 2>&1; then
		yum install -y python3 python3-venv python3-devel gcc make
	else
		echo "No supported package manager found; please ensure python3 and venv are installed." >&2
		exit 1
	fi
fi

# Create virtual environment inside the persistent data directory
VENV_DIR="$DATA_DIR/venv"
if [ -d "$VENV_DIR" ]; then
	echo "Using existing virtualenv at $VENV_DIR"
else
	echo "Creating virtualenv at $VENV_DIR"
	python3 -m venv "$VENV_DIR"
fi

# Activate and upgrade pip
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel

# Install requirements from repository
REQ_FILE="$REPO_ROOT/requirements.txt"
if [ -f "$REQ_FILE" ]; then
	echo "Installing Python requirements from $REQ_FILE"
	pip install --no-cache-dir -r "$REQ_FILE"
else
	echo "No requirements.txt found at $REQ_FILE; skipping pip install."
fi

echo "Setup complete. To use the environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo "If running in Docker, mount your host persistent path at $DATA_DIR. Example:"
echo "  docker run --rm -v /mnt/data/szeyap-bot-files:$DATA_DIR -v \$(pwd):/workspace -w /workspace python:3.11 /bin/bash -c 'scripts/docker-linux-ephemeral-install.sh'"

deactivate || true

