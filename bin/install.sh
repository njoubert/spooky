#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}/etc/

#
#cp spooky.conf /etc/init/spooky.conf
#initctl reload-configuration


mkdir -p /logs && \
	mkdir -p /tmp && \
	cp spooky.service /lib/systemd/system/spooky.service && \
	systemctl enable NetworkManager-wait-online.service && \
	systemctl enable systemd-networkd-wait-online.service && \
	ln -s /lib/systemd/system/spooky.service /lib/systemd/system/network-online.target.wants/ && \
	systemctl daemon-reload && \
	systemctl enable spooky.service


