#!/bin/bash

# start virtual environment
echo "[II] python init"

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
