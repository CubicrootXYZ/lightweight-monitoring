FROM python:3.9
COPY . /app

CMD python3 /app/monitoring.py