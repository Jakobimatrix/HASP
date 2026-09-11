#!/usr/bin/env bash
set -euo pipefail
# Create Python venv at repo root and install migration requirements

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "Upgrading pip and installing requirements"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$REQ_FILE"

echo "venv created. Run $VENV_DIR/bin/python <your_script>"
