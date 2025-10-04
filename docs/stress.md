### Stress Test Python Script:
```
cd ./stress-test

python app_ingress_load.py \
  --duration 120 \
  --rps 40 \
  --mix 0.5 0.25 0.25 \
  --error-rate 0.15 --error-5xx-code 500 \
  --latency-ms 10 300 --latency-code 200 \
  --frontend http://localhost \
  --errors   http://localhost/api \
  --latency  http://localhost/latency

# Watch Grafana Dashboard for reaction
```