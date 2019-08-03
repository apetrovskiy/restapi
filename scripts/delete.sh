#!/bin/sh

sudo service mongod stop
sudo apt-get purge mongodb-org*
sudo rm -r /var/log/mongodb
sudo rm -r /var/lib/mongodb

sudo service restapi stop
sudo rm -r ~/restapi/

sudo apt-get purge python3.7
sudo apt-get purge virtualenv

echo --------------------
echo Done
