#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}/etc/

#
#cp spooky.conf /etc/init/spooky.conf
#initctl reload-configuration


mkdir -p /logs && mkdir -p /tmp && cp spooky.service /lib/systemd/system/spooky.service && systemctl daemon-reload && systemctl enable spooky.service


