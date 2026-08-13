FROM python:3.12-slim

WORKDIR /app

COPY ingestion/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared ./shared
COPY ingestion ./ingestion

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "ingestion.run_all"]
