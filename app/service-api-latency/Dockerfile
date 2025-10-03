FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV SERVICE_NAME=api-latency
ENV APP_PORT=8082

EXPOSE 8082

HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD curl -fsS http://localhost:8082/healthz || exit 1

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8082"]
