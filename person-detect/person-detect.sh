#!/bin/bash

set -e

PROJECT_HOME="/opt/blink-gadget"
VENV="$PROJECT_HOME/venv"
PYTHON="$VENV/bin/python"

SCRIPT="$PROJECT_HOME/person-detect.py"

if [[ ! -d "$VENV" || ! -x "$PYTHON" ]]; then
  echo "Virtual environment not found at: $VENV"
  exit 1
fi

# Run using the venv's python - no need to source/activate/deactivate
"$PYTHON" "$SCRIPT" --input /media --output /srv/www/images --preserve --recursive --quiet
