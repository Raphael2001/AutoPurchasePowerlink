From python:3.8

Run pip install Flask gunicorn flask_restful flask_cors requests

COPY src/ /app

WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
