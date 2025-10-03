import requests

def test_errors_runtime_smoke(wait_errors, errors_base_url):
    # Happy path
    ok = requests.get(f"{errors_base_url}/api", timeout=5)
    assert ok.status_code == 200

    # Forced error
    bad = requests.get(f"{errors_base_url}/api?code=500", timeout=5)
    assert bad.status_code == 500

    # Metrics present
    m = requests.get(f"{errors_base_url}/metrics", timeout=5)
    assert m.status_code == 200
    assert "http_requests_total" in m.text
