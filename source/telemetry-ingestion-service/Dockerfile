FROM python:3.11-slim

WORKDIR /app

COPY telemetry_consumer.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "telemetry_consumer.py"]
