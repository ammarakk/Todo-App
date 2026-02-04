# Phase 5 Production Deployment Guide

**Version**: 1.0
**Last Updated**: 2026-02-04
**Environment**: Production (Kubernetes)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [SSL/TLS Configuration](#ssltls-configuration)
4. [Application Deployment](#application-deployment)
5. [Database Setup](#database-setup)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling Configuration](#scaling-configuration)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Kubernetes**: v1.25+ (Minikube for local, AKS/GKE/EKS for production)
- **Helm**: v3.0+
- **kubectl**: Match Kubernetes version
- **Dapr CLI**: v1.12+
- **PostgreSQL**: v14+ (or Neon Cloud)
- **Domain**: Custom domain for TLS certificates
- **Cloud Provider**: AWS, GCP, or Azure account

### Required Accounts

1. **Kubernetes Cluster** (AKS/GKE/EKS or Minikube)
2. **Container Registry** (Docker Hub, GHCR, ECR, GCR)
3. **S3-Compatible Storage** (AWS S3, MinIO, Wasabi)
4. **Email Service** (SendGrid, AWS SES) - optional for reminders
5. **DNS Provider** (Route53, Cloudflare, Google DNS)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/todo-app.git
cd todo-app/phase-5
```

### 2. Create Namespace

```bash
kubectl create namespace phase-5
kubectl create namespace cert-manager
kubectl create namespace monitoring
```

### 3. Install Dapr

```bash
dapr init --runtime-version 1.12 --helm-chart
dapr dashboard --port 8080
```

### 4. Install NGINX Ingress Controller

```bash
# For Minikube
minikube addons enable ingress

# For production (Helm)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

### 5. Install cert-manager (for TLS)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Verify installation
kubectl get pods -n cert-manager
```

### 6. Install Prometheus & Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values monitoring/prometheus-values.yaml

# Install Grafana
kubectl apply -f monitoring/grafana.yaml
```

---

## SSL/TLS Configuration

### 1. Update Domain Names

Edit `k8s/tls-ingress.yaml` and replace `yourdomain.com` with your actual domain:

```yaml
spec:
  tls:
  - hosts:
    - api.todo-app.yourdomain.com  # UPDATE THIS
    secretName: backend-api-tls-secret
```

### 2. Update Email for Let's Encrypt

Edit `k8s/certificate-manager.yaml`:

```yaml
spec:
  acme:
    email: admin@yourdomain.com  # UPDATE THIS
```

### 3. Apply Certificate Configuration

```bash
# Apply ClusterIssuer (staging first)
kubectl apply -f k8s/certificate-manager.yaml

# Verify ClusterIssuer
kubectl get clusterissuer -n phase-5

# Apply TLS Ingress
kubectl apply -f k8s/tls-ingress.yaml

# Verify certificates
kubectl get certificate -n phase-5
kubectl describe certificate backend-api-tls -n phase-5
```

### 4. Verify TLS

```bash
# Check certificate status
kubectl get secrets -n phase-5 | grep tls

# Test HTTPS connection
curl -I https://api.todo-app.yourdomain.com/health
```

---

## Application Deployment

### 1. Build and Push Docker Images

```bash
# Build backend image
cd backend
docker build -t todo-app-backend:v1.0 .
docker tag todo-app-backend:v1.0 YOUR_REGISTRY/todo-app-backend:v1.0
docker push YOUR_REGISTRY/todo-app-backend:v1.0

# Build notification service image
cd ../microservices/notification
docker build -t todo-app-notification:v1.0 .
docker tag todo-app-notification:v1.0 YOUR_REGISTRY/todo-app-notification:v1.0
docker push YOUR_REGISTRY/todo-app-notification:v1.0
```

### 2. Create Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=YOUR_PASSWORD \
  --from-literal=host=postgres.postgres.svc.cluster.local \
  --namespace=phase-5

# Ollama service
kubectl create secret generic ollama-config \
  --from-literal=host=http://ollama.phase-5.svc.cluster.local:11434 \
  --namespace=phase-5

# AWS credentials (for backups)
kubectl create secret generic aws-credentials \
  --from-literal=access-key-id=YOUR_ACCESS_KEY \
  --from-literal=secret-access-key=YOUR_SECRET_KEY \
  --namespace=phase-5

# SendGrid API key (for email reminders)
kubectl create secret generic sendgrid-config \
  --from-literal=api-key=YOUR_SENDGRID_API_KEY \
  --namespace=phase-5
```

### 3. Deploy Using Helm

```bash
# Update image values in helm/backend/values.yaml
# image:
#   repository: YOUR_REGISTRY/todo-app-backend
#   tag: "v1.0"

# Install backend
helm install backend helm/backend \
  --namespace phase-5 \
  --values helm/backend/values-production.yaml

# Install notification service
helm install notification helm/notification \
  --namespace phase-5 \
  --values helm/notification/values-production.yaml

# Verify deployments
kubectl get deployments -n phase-5
kubectl get pods -n phase-5
```

### 4. Deploy Kafka (Redpanda)

```bash
cd kafka
docker-compose up -d

# Verify topics
docker exec redpanda-1 rpk topic list
```

---

## Database Setup

### 1. Deploy PostgreSQL

```bash
# Using Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --namespace phase-5 \
  --set auth.password=YOUR_PASSWORD \
  --set persistence.enabled=true

# Or use Neon Cloud (managed PostgreSQL)
# Update DATABASE_URL in backend/config.py
```

### 2. Run Migrations

```bash
# Get backend pod
BACKEND_POD=$(kubectl get pod -n phase-5 -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run database initialization
kubectl exec -n phase-5 ${BACKEND_POD} -- python scripts/init_db.py
```

### 3. Verify Database Connection

```bash
# Port forward to backend
kubectl port-forward -n phase-5 deployment/backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health
```

---

## Monitoring & Alerting

### 1. Access Prometheus

```bash
# Port forward
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Open browser
open http://localhost:9090
```

### 2. Access Grafana

```bash
# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Default credentials
Username: admin
Password: prom-operator

# Open browser
open http://localhost:3000
```

### 3. Import Dashboards

Navigate to Grafana → Dashboards → Import and import:
- `monitoring/dashboards/backend-dashboard.json`
- `monitoring/dashboards/kafka-dashboard.json`

### 4. Configure Alerting

Edit `monitoring/alert-rules.yaml` with your alert endpoints (Slack, PagerDuty):

```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

Apply alerting rules:

```bash
kubectl apply -f monitoring/alert-rules.yaml
```

---

## Backup & Recovery

### 1. Configure Automated Backups

```bash
# Update S3 bucket in k8s/backup-cronjob.yaml
# Apply backup CronJob
kubectl apply -f k8s/backup-cronjob.yaml

# Verify CronJob
kubectl get cronjob -n phase-5
kubectl logs -n phase-5 job/database-backup-<timestamp>
```

### 2. Manual Backup

```bash
chmod +x scripts/backup-database.sh
./scripts/backup-database.sh snapshot
```

### 3. Restore from Backup

```bash
./scripts/backup-database.sh restore todo-app-backup-20260204_020000.sql.gz
```

---

## Scaling Configuration

### 1. Horizontal Pod Autoscaler

```bash
# Apply HPA
kubectl apply -f k8s/autoscaler.yaml

# Verify HPA
kubectl get hpa -n phase-5

# View HPA status
kubectl describe hpa backend-hpa -n phase-5
```

### 2. Manual Scaling

```bash
# Scale backend to 5 replicas
kubectl scale deployment backend --replicas=5 -n phase-5

# Verify
kubectl get pods -n phase-5
```

### 3. Cluster Autoscaling

```bash
# For AKS
az aks update --resource-group myResourceGroup --name myAKSCluster --enable-cluster-autoscaler --min-count 3 --max-count 10

# For GKE
gcloud container clusters update my-cluster --enable-autoscaling --min-nodes 3 --max-nodes 10
```

---

## Security Hardening

### 1. Verify No Hardcoded Secrets

```bash
# Search for secrets in code
grep -r "password\|api_key\|secret" backend/src/ --exclude-dir=__pycache__
```

### 2. Verify All Secrets Use Kubernetes Secrets

```bash
# List all secrets
kubectl get secrets -n phase-5

# Verify no secrets in ConfigMaps
kubectl get configmaps -n phase-5 -o yaml | grep -i "password\|api_key"
```

### 3. Verify TLS/mTLS

```bash
# Check TLS certificates
kubectl get certificates -n phase-5
kubectl describe certificate backend-api-tls -n phase-5

# Verify NetworkPolicy for TLS-only traffic
kubectl get networkpolicies -n phase-5
```

### 4. Verify Input Validation

```bash
# Run security tests
pytest tests/security/test_input_validation.py
pytest tests/security/test_sql_injection.py
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n phase-5

# Describe pod
kubectl describe pod <pod-name> -n phase-5

# View logs
kubectl logs <pod-name> -n phase-5

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n phase-5
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl get pods -n phase-5 -l app=postgres

# Test connection
kubectl exec -it <backend-pod> -n phase-5 -- psql ${DATABASE_URL}

# Check secrets
kubectl describe secret db-credentials -n phase-5
```

### SSL/TLS Issues

```bash
# Check certificate status
kubectl get certificate -n phase-5
kubectl describe certificate backend-api-tls -n phase-5

# View cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check ingress controller
kubectl get svc -n ingress-nginx
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Performance Issues

```bash
# Check HPA status
kubectl get hpa -n phase-5
kubectl describe hpa backend-hpa -n phase-5

# View resource usage
kubectl top pods -n phase-5
kubectl top nodes

# Check metrics in Prometheus
open http://localhost:9090
```

---

## Rollback Procedure

### 1. Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/backend -n phase-5

# Rollback to previous version
kubectl rollout undo deployment/backend -n phase-5

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n phase-5
```

### 2. Rollback Helm Release

```bash
# View history
helm history backend -n phase-5

# Rollback
helm rollback backend 1 -n phase-5
```

---

## Maintenance Windows

### Scheduled Maintenance

```bash
# Scale down to zero
kubectl scale deployment backend --replicas=0 -n phase-5

# Perform maintenance
# ...

# Scale back up
kubectl scale deployment backend --replicas=3 -n phase-5
```

---

## Support & Contacts

- **Documentation**: `docs/`
- **Issues**: GitHub Issues
- **On-Call**: PagerDuty
- **Slack**: #todo-app-ops

---

**Last Updated**: 2026-02-04
**Version**: 1.0
**Maintained By**: DevOps Team
