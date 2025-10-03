import requests

def test_frontend_runtime_smoke(wait_frontend, frontend_base_url):
    # Root serves HTML
    r = requests.get(f"{frontend_base_url}/", timeout=5)
    assert r.status_code == 200
    # Metrics endpoint present
    m = requests.get(f"{frontend_base_url}/metrics", timeout=5)
    assert m.status_code == 200
    assert "http_requests_total" in m.text
