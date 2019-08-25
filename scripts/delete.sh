#!/bin/sh

sudo service restapi stop
sudo rm -r ~/restapi/

sudo systemctl daemon-reload

echo --------------------
echo Done
