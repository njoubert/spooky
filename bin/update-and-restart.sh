#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}

systemctl stop spooky.service
git pull
find . -name "*.pyc" | xargs rm
./bin/install.sh
systemctl start spooky.service


