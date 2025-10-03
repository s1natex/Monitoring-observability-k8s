## Local Docker-Compose start up  and test:
### - Using Docker Desktop Run:
```
docker compose up --build
```
### - Access each service with local Docker-Compose Run:
    - **frontend traffic** -- `http://localhost:8080/` -- `/metrics`, `/healthz`
    - **errors API** -- `http://localhost:8081/api` -- `/metrics`, `/healthz`
    - **latency API** -- `http://localhost:8082/latency` -- `/metrics`, `/healthz`
### - Run Tests Locally Docker-Compose:
```
cd root
python -m pip install -r requirements-dev.txt  # Install deps

cd app
python -m pytest -q  # to run all of them

# for smoke tests at runtime:
python -m pytest -q tests/service-frontend-traffic/test_smoke_frontend_traffic.py \
                   tests/service-api-errors/test_smoke_api_errors.py \
                   tests/service-api-latency/test_smoke_api_latency.py
```