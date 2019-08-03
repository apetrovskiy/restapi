#!/bin/sh

wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

sudo systemctl start mongod
sudo systemctl enable mongod

sudo apt-get install python3.7
sudo apt-get install virtualenv

virtualenv -p python3.7 ~/restapi/venv
. restapi/venv/bin/activate
python --version
pip -V
pip install -e ~/restapi
deactivate

sudo cp ~/restapi/scripts/restapi.service /etc/systemd/system/restapi.service
sudo systemctl start restapi
sudo systemctl enable restapi

echo --------------------
echo Done
