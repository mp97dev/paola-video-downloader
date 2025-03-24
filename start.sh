#!/bin/bash

echo -e "\033[0;32mInstalling Firefox browser and geckodriver...\033[0m"
sudo apt-get install -y firefox-geckodriver

echo -e "\033[0;32mInstalling xattr package...\033[0m"
sudo apt-get install -y xattr

# start virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip3 install -r requirements.txt

# run the application
python3 src/app.py