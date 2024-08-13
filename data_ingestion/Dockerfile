# backend/data_ingestion/Dockerfile
FROM python:3.11

WORKDIR /data_ingestion

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "data_ingestion.celery_app", "worker", "--loglevel=info"]