FROM python:2.7

ADD requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ADD src /app
ADD entrypoint.sh /entryoint
ADD config_example.yaml /config.yaml
ADD uwsgi.ini /uwsgi.ini

ENV CONFIG_FILE_PATH "/config.yaml"

VOLUME ["/data"]
EXPOSE 8080

WORKDIR /app

ENTRYPOINT ["/entryoint"]
