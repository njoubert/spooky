#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}/etc/

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [[ $1 = 'remove' ]]
then

	echo 'removing spooky odroidperson systemd service'

	systemctl stop spooky.service && \
		systemctl disable spooky.service && \
		rm -f /lib/systemd/system/network-online.target.wants/spooky.service && \
		rm -f /lib/systemd/system/spooky.service && \
		systemctl daemon-reload
	systemctl enable NetworkManager-wait-online.service

else

	echo 'installing spooky odroidperson systemd service'

	mkdir -p /logs && \
		mkdir -p /tmp && \
		cp spooky.service /lib/systemd/system/spooky.service && \
		systemctl daemon-reload && \
		systemctl enable spooky.service
		systemctl start spooky.service
	systemctl enable NetworkManager-wait-online.service

fi





