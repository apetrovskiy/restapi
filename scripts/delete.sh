#!/bin/sh

sudo service restapi stop
sudo rm /etc/systemd/system/restapi.service
sudo rm -r /opt/restapi/

sudo systemctl daemon-reload

echo --------------------
echo Done
