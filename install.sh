#!/bin/bash
set -e

echo "[II] python init"
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

if git rev-parse --git-dir >/dev/null 2>&1; then
    ./scripts/install-hooks.sh || echo "[WW] could not install git hooks"
fi
