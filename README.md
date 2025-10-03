# Monitoring and observability implementation Project

## [Project Page](https://roadmap.sh/projects/simple-monitoring-dashboard)



## Instructions to Run and Test:
### Local Docker-Compose:
- Using Docker Desktop Run:
```
docker compose up --build
```
- Access each service with local Docker-Compose Run:
    - **frontend traffic** -- `http://localhost:8080/` -- `/metrics`, `/healthz`
    - **errors API** -- `http://localhost:8081/api` -- `/metrics`, `/healthz`
    - **latency API** -- `http://localhost:8082/latency` -- `/metrics`, `/healthz`
- Run Tests Locally Docker-Compose:
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
### Local Docker Desktop k8s Cluster:
- Create namespaces:
```
kubectl apply -f k8s/namespaces.yaml
```
- Install metrics-server:
```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
- Install ingress-nginx (ingress controller):
```
kubectl create namespace ingress-nginx || true
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.metrics.enabled=true

# Verify the controller is ready
kubectl wait -n ingress-nginx --for=condition=Available deploy/ingress-nginx-controller --timeout=180s
kubectl get pods -n ingress-nginx -o wide
kubectl get svc -n ingress-nginx
```
- Deploy Cluster:
```
kubectl apply -f k8s/apps/deployments.yaml
kubectl apply -f k8s/apps/services.yaml
kubectl apply -f k8s/apps/hpas.yaml
kubectl apply -f k8s/apps/ingress-apps.yaml
```
- Install and run Argo CD:
```
kubectl apply -n utils -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Make the server run in HTTP mode (no TLS) for localhost:
kubectl apply -f k8s/utils/argocd-cmd-params-cm.yaml

# Restart Argo CD server to pick up the config:
kubectl -n utils rollout restart deploy argocd-server

# Expose via Ingress:
kubectl apply -f k8s/utils/ingress-utils.yaml

# Point ArgoCD to correct NameSpace
kubectl apply -f k8s/utils/argocd-rbac-fixes.yaml
kubectl apply -f k8s/utils/argocd-webhook-rbac.yaml
kubectl -n utils rollout restart statefulset argocd-application-controller || \
kubectl -n utils rollout restart deploy argocd-application-controller
```
- Install Prometheus & Grafana using Helm:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install promstack prometheus-community/kube-prometheus-stack \
  --namespace utils --create-namespace \
  -f k8s/utils/monitoring/values-prom-stack.yaml
```
- Run Argo CD Application:
```
kubectl apply -f argocd/app.yaml
```
- After Pods are Ready:
##### **App**
```
Frontend: http://localhost/ -- `/metrics`, `/healthz`
Errors API: http://localhost/api -- `/metrics`, `/healthz`
Latency API: http://localhost/latency -- `/metrics`, `/healthz`
```
##### **Prometheus and Grafana**
```
Prometheus: http://prometheus.localhost/
Grafana: http://grafana.localhost/

# admin / admin
```
##### **Argo CD**
```
http://argocd.localhost/

# admin
# password
kubectl -n utils get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```
- Apply Prometheus, Grafana and alertmanager configs:
```
# Apply
kubectl apply -f k8s/utils/monitoring/servicemonitors.yaml
kubectl apply -f k8s/utils/monitoring/prometheusrule-app-alerts.yaml
kubectl apply -f k8s/utils/monitoring/alertmanager-config.yaml
kubectl apply -f k8s/utils/monitoring/grafana-dashboard.yaml
kubectl apply -f k8s/utils/monitoring/grafana-dashboard-all-in-one.yaml
```
### if metrics-server isn’t Ready -- Patch:
```
kubectl -n kube-system patch deploy metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

kubectl -n kube-system patch deploy metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/ports","value":[{"containerPort":10250,"name":"https"}]}]'

kubectl -n kube-system rollout status deploy/metrics-server
kubectl -n kube-system get pods -l k8s-app=metrics-server -o wide
kubectl get apiservices | grep metrics
kubectl top nodes
kubectl top pods -A
```
- Clean Up:
```
# Remove app + utils workloads
kubectl delete -f k8s/apps/ingress-apps.yaml
kubectl delete -f k8s/apps/hpas.yaml
kubectl delete -f k8s/apps/services.yaml
kubectl delete -f k8s/apps/deployments.yaml

# Remove Argo CD app, ingress
kubectl delete -f argocd/app.yaml --ignore-not-found
kubectl delete -f k8s/utils/ingress-utils.yaml --ignore-not-found
kubectl delete -n utils -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Remove prometheus stack
helm uninstall promstack -n utils

# Remove ingress-nginx
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete ns ingress-nginx --ignore-not-found

# Remove metrics-server
kubectl delete -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# namespaces
kubectl delete ns app utils
```
