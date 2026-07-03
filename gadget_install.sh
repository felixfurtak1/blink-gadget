#!/bin/bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root (use sudo $0)." >&2
    exit 1
fi

# Gadget install location
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc"

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

echo "Installation complete!"
