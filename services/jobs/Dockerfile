FROM python:3.8
RUN pip install requests tqdm sparqlwrapper

# Prepare directories and volumes
RUN mkdir /scripts
RUN mkdir /dotenv
RUN touch /dotenv/.env
VOLUME /dotenv/.env
VOLUME /static
WORKDIR /scripts

# Install task runner (http://taskfile.dev)
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Run idling
ENTRYPOINT tail -f /dev/null