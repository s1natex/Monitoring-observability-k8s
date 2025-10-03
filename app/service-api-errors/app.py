import os
import time
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

SERVICE_NAME = os.getenv("SERVICE_NAME", "api-errors")
APP_PORT = int(os.getenv("APP_PORT", "8081"))

app = FastAPI(title=SERVICE_NAME)

REQ_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "route", "status"],
)
INF_FLIGHT = Gauge("in_flight_requests", "In-flight requests", ["service"])
REQ_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency seconds",
    ["service", "route", "method"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
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

@app.get("/api")
async def api(code: Optional[int] = None, rate: Optional[float] = None):
    """
    Returns 200 by default.
    - ?code=500 forces a status code.
    - ?rate=0.2 fails probabilistically with 500 (unless 'code' provided).
    """
    status = 200
    if code is not None:
        status = code
    elif rate is not None and 0.0 < rate < 1.0:
        import random
        if random.random() < rate:
            status = 500

    payload = {"service": SERVICE_NAME, "status": status}
    return JSONResponse(payload, status_code=status)

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok", status_code=200)

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
