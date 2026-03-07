FROM python:3.11-slim

WORKDIR /app

COPY rule_engine.py .
COPY db.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "rule_engine.py"]