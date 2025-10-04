import os
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

SERVICE_NAME = os.getenv("SERVICE_NAME", "frontend-traffic")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

app = FastAPI(title=SERVICE_NAME)

# ---- Use a service-scoped registry to avoid duplicate metric registration in tests ----
REGISTRY = CollectorRegistry()

REQ_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "route", "status"],
    registry=REGISTRY,
)
INF_FLIGHT = Gauge(
    "in_flight_requests",
    "In-flight requests",
    ["service"],
    registry=REGISTRY,
)
REQ_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency seconds",
    ["service", "route", "method"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
    registry=REGISTRY,
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next: Callable):
    route = request.url.path
    method = request.method
    INF_FLIGHT.labels(service=SERVICE_NAME).inc()
    start = time.perf_counter()
    status_code = 500
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        elapsed = time.perf_counter() - start
        REQ_LATENCY.labels(SERVICE_NAME, route, method).observe(elapsed)
        REQ_COUNTER.labels(SERVICE_NAME, method, route, str(status_code)).inc()
        INF_FLIGHT.labels(service=SERVICE_NAME).dec()

@app.get("/", response_class=HTMLResponse)
async def index():
    html = f"""
    <html>
      <head><title>{SERVICE_NAME}</title></head>
      <body>
        <h1>{SERVICE_NAME}</h1>
        <p>Metrics at <code>/metrics</code>, health at <code>/healthz</code>.test(2)</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok", status_code=200)

@app.get("/metrics")
async def metrics():
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
