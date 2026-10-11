#!/usr/bin/env bash

# brief:
#   Clones and setup the doo-camera Python script
# note:
#   Should be executed by a one-shot systemd service

# Exit on errors, treat unset variables as errors, and propagate failures through pipelines.
set -Eeuo pipefail

REPO_URL="https://github.com/bastien-sagetat/door-camera.git"
APP_DIR="/opt/door-camera/repo"
BRANCH="bsa/add-software"

echo "Removing old repository..."
rm -rf -- "$APP_DIR"

echo "Cloning repository..."
mkdir -p "$(dirname "$APP_DIR")"
git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$APP_DIR"

cd "$APP_DIR/soft"

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Installing Python requirements..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Setup completed successfully."
