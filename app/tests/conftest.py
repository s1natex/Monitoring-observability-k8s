import os
import time
from typing import Callable

import pytest
import requests


# ---- Runtime (smoke) helpers ----

def _wait_for(url: str, timeout: float = 30.0, interval: float = 0.5) -> None:
    """
    Poll a URL until it returns HTTP 200 or timeout.
    Raises AssertionError if not ready in time.
    """
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return
            last_err = AssertionError(f"Got {r.status_code} from {url}")
        except Exception as e:
            last_err = e
        time.sleep(interval)
    raise AssertionError(f"Service not ready: {url}: {last_err}")

@pytest.fixture(scope="session")
def frontend_base_url() -> str:
    port = int(os.getenv("FRONTEND_PORT", "8080"))
    return f"http://localhost:{port}"

@pytest.fixture(scope="session")
def errors_base_url() -> str:
    port = int(os.getenv("ERRORS_PORT", "8081"))
    return f"http://localhost:{port}"

@pytest.fixture(scope="session")
def latency_base_url() -> str:
    port = int(os.getenv("LATENCY_PORT", "8082"))
    return f"http://localhost:{port}"

@pytest.fixture(scope="session", autouse=False)
def wait_frontend(frontend_base_url):
    _wait_for(f"{frontend_base_url}/healthz")

@pytest.fixture(scope="session", autouse=False)
def wait_errors(errors_base_url):
    _wait_for(f"{errors_base_url}/healthz")

@pytest.fixture(scope="session", autouse=False)
def wait_latency(latency_base_url):
    _wait_for(f"{latency_base_url}/healthz")
