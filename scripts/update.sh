#!/bin/sh

sudo systemctl stop restapi
git pull restapi
~/restapi/venv/bin/activate
pip install -e .
deactivate
sudo systemctl start restapi

echo --------------------
echo Done
