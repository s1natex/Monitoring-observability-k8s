import requests

def test_latency_runtime_smoke(wait_latency, latency_base_url):
    # Happy path with small delay
    r = requests.get(f"{latency_base_url}/latency?ms=25", timeout=5)
    assert r.status_code == 200
    # Metrics present
    m = requests.get(f"{latency_base_url}/metrics", timeout=5)
    assert m.status_code == 200
    assert "http_request_duration_seconds_bucket" in m.text
