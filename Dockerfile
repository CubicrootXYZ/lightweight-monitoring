FROM python:3.9
COPY . /app

CMD python /app/monitoring.py