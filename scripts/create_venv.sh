#!/usr/bin/env bash
set -euo pipefail
# Create Python venv at repo root and install migration requirements

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

# If venv exists and contains python, skip creation
if [ -x "$VENV_DIR/bin/python" ]; then
	echo "Virtualenv exists at: $VENV_DIR -> skipping creation"
else
	echo "Creating virtualenv at: $VENV_DIR"
	python3 -m venv "$VENV_DIR"
fi

echo "Upgrading pip and installing requirements"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$REQ_FILE"

echo "venv created. Run $VENV_DIR/bin/python <your_script>"
