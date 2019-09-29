#!/bin/sh

sudo systemctl stop restapi
cd /opt/restapi || { echo "Failure"; exit 1; }
git pull
. venv/bin/activate
pip install -e .
deactivate
sudo systemctl daemon-reload
sudo systemctl start restapi

echo --------------------
echo Done
