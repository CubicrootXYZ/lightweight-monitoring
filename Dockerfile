FROM python:3.9
COPY . /app
RUN pip install yaml

CMD python3 /app/monitoring.py