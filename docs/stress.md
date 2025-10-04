- ### Cluster Stress Test with a Python Script:
```
cd ./stress-test/

python app_ingress_load.py \
  --duration 120 \
  --rps 40 \
  --mix 0.5 0.25 0.25 \
  --error-rate 0.15 --error-5xx-code 500 \
  --latency-ms 10 300 --latency-code 200 \
  --frontend http://localhost \
  --errors   http://localhost/api \
  --latency  http://localhost/latency

# Watch CLI for script results print
# Watch Grafana Dashboard for Live Dashboard reaction
```
- ### If needed generate 5xx errors for dashboards tests:
```
curl -i "http://localhost/api?code=500"
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost/api?code=500"
```
