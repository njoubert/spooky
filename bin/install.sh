#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}/etc/

#
#cp spooky.conf /etc/init/spooky.conf
#initctl reload-configuration

cp spooky.service /lib/systemd/system/spooky.service
systemctl dameon-reload
systemctl enable spooky.service


