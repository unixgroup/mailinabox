# Mail-in-a-Box Dockerfile
# see https://www.docker.io
###########################

# To build the image:
# sudo docker.io build -t mailinabox .

# Run your container.
#  -i -t: creates an interactive console so you can poke around (CTRL+D will terminate the container)
#  -p ...: Maps container ports to host ports so that the host begins acting as a Mail-in-a-Box.
# sudo docker.io run -i -t -p 22 -p 25:25 -p 53:53/udp -p 443:443 -p 587:587 -p 993:993 mailinabox

###########################################

# We need a better starting image than docker's ubuntu image because that
# base image doesn't provide enough to run most Ubuntu services. See
# http://phusion.github.io/baseimage-docker/ for an explanation.

FROM phusion/baseimage:0.9.12

# Dockerfile metadata.
MAINTAINER Joshua Tauberer (http://razor.occams.info)
EXPOSE 22 25 53 443 587 993

# Docker-specific Mail-in-a-Box configuration.
ENV DISABLE_FIREWALL 1
ENV NO_RESTART_SERVICES 1

# Add this repo into the image so we have the configuration scripts
# so we can determine what packages to pre-install.
ADD tools /usr/local/mailinabox/tools
ADD setup /usr/local/mailinabox/setup

# Pre-load all of the packages we'll need.
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y $(python3 /usr/local/mailinabox/tools/list_all_packages.py /usr/local/mailinabox)

# Add the remainder of the files we'll need. Defer these so Docker
# can cache as much as possible.
ADD conf /usr/local/mailinabox/conf
ADD management /usr/local/mailinabox/management
ADD containers /usr/local/mailinabox/containers

# We can't know things like the IP address where the container will eventually
# be deployed until the container is started. We also don't want to create any
# private keys during the creation of the image --- that should wait until the
# container is started too. So our whole setup process is deferred until the
# container is started.
CMD ["/usr/local/mailinabox/containers/docker/container_start.sh"]
