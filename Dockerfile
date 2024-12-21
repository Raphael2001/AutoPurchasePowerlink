FROM python:3.11-slim-buster

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

COPY requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt
RUN pip install gunicorn

COPY src/ src/

WORKDIR /src

ENV PYTHONPATH /

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 Main.Main:app








