#!/bin/bash

set -euo pipefail

# Find the directory of this script and change to it
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root (use sudo $0)." >&2
    exit 1
fi

# Capture the user who invoked sudo
ORIGINAL_USER="${SUDO_USER:-$USER}"

# Gadget install location
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc"

# Python project location
PROJECT_HOME="/opt/blink-gadget"
VENV="$PROJECT_HOME/venv"
PIPTEMP="$PROJECT_HOME/tmp"

# Image web serve location
WWW="/srv/www"

# Root-level operations
echo "Installing scripts and config..."
cp gadget/mirror "$INSTALL_DIR"
cp gadget/gadget "$INSTALL_DIR"
cp gadget/gadget-config "$CONFIG_DIR"

echo "Making scripts executable..."
chmod 755 "$INSTALL_DIR/mirror"
chmod 755 "$INSTALL_DIR/gadget"

echo "Adjusting gadget-config permissions..."
chmod 644 "$CONFIG_DIR/gadget-config"

echo "Creating project directory $PROJECT_HOME..."
mkdir -p "$PROJECT_HOME"

echo "Creating image thumbnail directory $WWW..."
mkdir -p "$WWW"

echo "Changing ownership of $PROJECT_HOME and $WWW to user: $ORIGINAL_USER..."
chown "$ORIGINAL_USER:$ORIGINAL_USER" "$PROJECT_HOME"
chown "$ORIGINAL_USER:$ORIGINAL_USER" "$WWW"

# Switch to current user for venv and pip operations
echo "Setting up Python virtual environment as user: $ORIGINAL_USER..."

sudo -u "$ORIGINAL_USER" -H bash << EOF
# Create the temp directory in userspace
mkdir -p "$PIPTEMP"

python3 -m venv "$VENV"

# Array of packages to install individually
declare -a PACKAGES=(
  "pip"
  "torch --index-url https://download.pytorch.org/whl/cpu --no-deps"
  "torchvision --index-url https://download.pytorch.org/whl/cpu --no-deps"
  "ultralytics-opencv-headless --no-deps"
  "opencv-python-headless --no-deps"
  "numpy --no-deps"
  "typing_extensions --no-deps"
  "pillow --no-deps"
  "PyYAML --no-deps"
  "matplotlib --no-deps"
  "packaging --no-deps"
  "pyparsing --no-deps"
  "cycler --no-deps"
  "python-dateutil --no-deps"
  "kiwisolver --no-deps"
  "fonttools --no-deps"
  "six --no-deps"
  "sympy --no-deps"
  "mpmath --no-deps"
)

echo "Installing and upgrading pip..."
TMPDIR="$PIPTEMP" "$VENV/bin/pip" install --upgrade pip

# Install remaining packages one by one
for package in "\${PACKAGES[@]:1}"; do
  echo "Installing: \$package"
  TMPDIR="$PIPTEMP" "$VENV/bin/pip" install \$package
done

echo "Copying person-detection scripts to $PROJECT_HOME..."
cp person-detect/* "$PROJECT_HOME"

echo "Making person-detection scripts executable..."
chmod 755 "$PROJECT_HOME/person-detect.py"
chmod 755 "$PROJECT_HOME/person-detect.sh"

echo "Creating services directory in $PROJECT_HOME..."
mkdir -p "$PROJECT_HOME/services"

cp services/* "$PROJECT_HOME/services"

# Clean up pip cache and temporary files
echo "Cleaning up temporary files..."
rm -rf "$PIPTEMP"/*
rm -rf "$PIPTEMP"
"$VENV/bin/pip" cache purge
EOF

echo "Installation complete!"
