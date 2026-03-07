FROM python:3.11-slim

WORKDIR /app

COPY state_consumer.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "state_consumer.py"]