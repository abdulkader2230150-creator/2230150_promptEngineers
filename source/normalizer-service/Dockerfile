FROM python:3.11-slim

WORKDIR /app

COPY normalizer.py .
COPY test_normalizer.py .
COPY consumer.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "consumer.py"]