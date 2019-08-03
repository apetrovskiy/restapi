#!/bin/sh

sudo systemctl stop restapi
cd ~/restapi
git pull
. venv/bin/activate
pip install -e .
deactivate
cd ~
sudo systemctl start restapi

echo --------------------
echo Done
