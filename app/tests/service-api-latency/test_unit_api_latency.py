from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from fastapi.testclient import TestClient

# Find the nearest ancestor directory named "app"
CUR = Path(__file__).resolve()
APP_ROOT = next(p for p in CUR.parents if p.name == "app")

SERVICE_DIR = APP_ROOT / "service-api-latency"
APP_FILE = SERVICE_DIR / "app.py"

spec = spec_from_loader(
    "latency_app_module",
    SourceFileLoader("latency_app_module", str(APP_FILE)),
)
latency_app = module_from_spec(spec)  # type: ignore
assert spec.loader is not None
spec.loader.exec_module(latency_app)  # type: ignore


def test_latency_default_200():
    client = TestClient(latency_app.app)  # type: ignore[attr-defined]
    r = client.get("/latency")
    assert r.status_code == 200
    assert r.json().get("status") == 200


def test_latency_with_delay_and_code():
    client = TestClient(latency_app.app)  # type: ignore[attr-defined]
    r = client.get("/latency?ms=10&code=418")
    assert r.status_code == 418
    body = r.json()
    assert "delay_ms" in body
    assert body["delay_ms"] >= 0


def test_metrics_exposes_expected_names():
    client = TestClient(latency_app.app)  # type: ignore[attr-defined]
    client.get("/latency?ms=1")
    m = client.get("/metrics")
    assert m.status_code == 200
    body = m.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds_bucket" in body
    assert "in_flight_requests" in body


def test_healthz_ok():
    client = TestClient(latency_app.app)  # type: ignore[attr-defined]
    r = client.get("/healthz")
    assert r.status_code == 200
