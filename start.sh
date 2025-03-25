#!/bin/bash

# start virtual environment
print "[II] python init"

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt


# run the application
print "[II] start"
python3 src/app.py

print() {
echo -e "\033[0;32m$1\033[0m"
}