#!/bin/bash

echo "[II] update and upgrade"
sudo apt update
sudo apt install -y google-chrome-stable
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl -sS -o chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip -d /usr/local/bin/
chromedriver --version

# start virtual environment
echo "[II] python init"

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
