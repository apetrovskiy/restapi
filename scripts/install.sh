#!/bin/sh

wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

sudo systemctl start mongod
sudo systemctl enable mongod

sudo apt-get install -y python3.7
sudo apt-get install -y virtualenv

virtualenv -p python3.7 /opt/restapi/venv
. /opt/restapi/venv/bin/activate

pip install -e /opt/restapi
deactivate

sudo cp /opt/restapi/scripts/restapi.service /etc/systemd/system/restapi.service
sudo systemctl start restapi
sudo systemctl enable restapi

echo --------------------
echo Done
