FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install pyyaml

CMD python3 /app/monitoring.py