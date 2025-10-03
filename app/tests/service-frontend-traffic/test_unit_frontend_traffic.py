from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from fastapi.testclient import TestClient

# Find the nearest ancestor directory named "app"
CUR = Path(__file__).resolve()
APP_ROOT = next(p for p in CUR.parents if p.name == "app")

SERVICE_DIR = APP_ROOT / "service-frontend-traffic"
APP_FILE = SERVICE_DIR / "app.py"

spec = spec_from_loader(
    "frontend_app_module",
    SourceFileLoader("frontend_app_module", str(APP_FILE)),
)
frontend_app = module_from_spec(spec)  # type: ignore
assert spec.loader is not None
spec.loader.exec_module(frontend_app)  # type: ignore


def test_index_ok():
    client = TestClient(frontend_app.app)  # type: ignore[attr-defined]
    r = client.get("/")
    assert r.status_code == 200
    assert "metrics" in r.text.lower()


def test_metrics_exposes_expected_names():
    client = TestClient(frontend_app.app)  # type: ignore[attr-defined]
    client.get("/")  # ensure some traffic
    m = client.get("/metrics")
    assert m.status_code == 200
    body = m.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds_bucket" in body
    assert "in_flight_requests" in body


def test_healthz_ok():
    client = TestClient(frontend_app.app)  # type: ignore[attr-defined]
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.text.strip().lower() == "ok"
