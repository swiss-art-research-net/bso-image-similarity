FROM python:3.8

# Prepare directories and volumes
RUN mkdir /scripts
VOLUME /static
WORKDIR /scripts

# Run idling
ENTRYPOINT tail -f /dev/null