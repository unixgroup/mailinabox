#!/bin/bash

# Local configuration details were not known at the time the Docker
# image was created, so all setup is defered until the container
# is started. That's when this script runs.

# If we're not in an interactive shell, set defaults.
if [ ! -t 0 ]; then
	export PUBLIC_IP=auto
	export PUBLIC_IPV6=auto
	export PRIMARY_HOSTNAME=auto-easy
	export CSR_COUNTRY=US
fi

# Start configuration.
cd /usr/local/mailinabox
setup/start.sh
if [ ! $? ]; then
	exit 1
fi

# Once the configuration is complete, start the Unix init process
# provided by the base image. We're running as process 0, and
# /sbin/my_init needs to run as process 0, so use 'exec' to replace
# this shell process and not fork a new one. Nifty right?
exec /sbin/my_init -- bash
