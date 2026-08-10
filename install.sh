#!/bin/bash
set -e

echo "[II] python init"
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Local development convenience; never fatal (CI checkouts don't need hooks).
if [ -d .git ]; then
    ./scripts/install-hooks.sh || echo "[WW] could not install git hooks"
fi
