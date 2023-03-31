FROM python:3.9-slim

COPY requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt
RUN pip install gunicorn

COPY src/ src/

WORKDIR /src

ENV PYTHONPATH /

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 Main.Main:app
