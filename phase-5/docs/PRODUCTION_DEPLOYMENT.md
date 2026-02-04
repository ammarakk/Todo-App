# Production Deployment Guide - Phase 5

## Overview

This guide covers deploying the Phase 5 Todo Application to production with full monitoring, observability, and high availability.

## Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured
- Helm 3.x installed
- Domain name configured
- SSL certificates (or cert-manager)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Ingress / LoadBalancer                  │
│                  (SSL Termination, Routing)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Frontend   │ │   Backend    │ │  Chatbot     │
│   (Next.js)  │ │  (FastAPI)   │ │  (AI Agent)  │
└──────────────┘ └──────┬───────┘ └──────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │    Kafka     │ │    Dapr      │
│   (Neon DB)  │ │  (Redpanda)  │ │ (Sidecar)    │
└──────────────┘ └──────────────┘ └──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │ Notification │
                │   Service    │
                └──────────────┘
```

## Deployment Steps

### 1. Create Namespaces

```bash
kubectl create namespace phase-5
kubectl create namespace monitoring
kubectl create namespace kafka
```

### 2. Deploy Infrastructure

#### Kafka (Redpanda)

```bash
# Deploy Redpanda operator
kubectl apply -f https://github.com/redpanda-data/redpanda-operator/src/main/io/../../config/crd/bases/redpanda.vectorized.io_redpandas.yaml
kubectl apply -f https://github.com/redpanda-data/redpanda-operator/src/main/io/../../config/manager/deployment.yaml

# Deploy Redpanda cluster
kubectl apply -f phase-5/kafka/redpanda-cluster.yaml
```

#### Dapr

```bash
# Install Dapr
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm install dapr dapr/dapr \
  --namespace default \
  --set global.ha.enabled=true \
  --set global.ha.replicaCount=3
```

#### Monitoring Stack

```bash
# Deploy Prometheus
kubectl apply -f phase-5/monitoring/prometheus.yaml

# Deploy Grafana
kubectl apply -f phase-5/monitoring/grafana.yaml

# Deploy Alerting Rules
kubectl apply -f phase-5/monitoring/alert-rules.yaml
```

### 3. Deploy Application Services

#### Backend Service

```bash
# Using Helm
helm install backend phase-5/helm/backend/ \
  --namespace phase-5 \
  --create-namespace \
  --set image.repository=your-registry/backend \
  --set image.tag=v1.0.0 \
  --set replicas=3 \
  --set env.POSTGRES_URL="postgresql://user:pass@host:5432/db" \
  --set env.DAPR_HTTP_PORT="3500"
```

#### Notification Service

```bash
helm install notification phase-5/helm/notification/ \
  --namespace phase-5 \
  --set image.repository=your-registry/notification \
  --set secrets.email.apiKey=your-sendgrid-key \
  --set secrets.email.fromEmail=noreply@yourdomain.com
```

#### Chatbot Service

```bash
helm install chatbot phase-5/helm/chatbot/ \
  --namespace phase-5 \
  --set image.repository=your-registry/chatbot \
  --set env.OLLAMA_URL=http://ollama:11434
```

### 4. Configure Ingress

```bash
# Create TLS secret
kubectl create secret tls app-tls \
  --cert=path/to/cert.crt \
  --key=path/to/cert.key \
  --namespace phase-5

# Apply ingress
kubectl apply -f phase-5/k8s/ingress.yaml
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods --namespace phase-5

# Check services
kubectl get svc --namespace phase-5

# Check logs
kubectl logs -f deployment/backend --namespace phase-5

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 --namespace monitoring
# Open http://localhost:3000
# Login: admin / changeme123
```

## Environment Variables

### Backend Service

```yaml
POSTGRES_URL: "postgresql://user:pass@host:5432/dbname"
DAPR_HTTP_PORT: "3500"
LOG_LEVEL: "INFO"
APP_ENV: "production"
OLLAMA_URL: "http://ollama:11434"
```

### Notification Service

```yaml
EMAIL_API_KEY: "your-sendgrid-key"
FROM_EMAIL: "noreply@yourdomain.com"
DAPR_HTTP_PORT: "3500"
LOG_LEVEL: "INFO"
```

## Scaling

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: phase-5
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Apply HPA

```bash
kubectl apply -f phase-5/k8s/hpa.yaml
```

## Monitoring

### Key Metrics

- **Request Rate**: `rate(http_requests_total[5m])`
- **Error Rate**: `rate(http_requests_total{status="error"}[5m]) / rate(http_requests_total[5m])`
- **Latency**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Active Tasks**: `rate(tasks_created_total[5m])`
- **WebSocket Connections**: `sum(websocket_connections_active)`

### Accessing Grafana

```bash
# Port forward to access Grafana
kubectl port-forward svc/grafana 3000:3000 --namespace monitoring

# Open browser to http://localhost:3000
# Default credentials: admin / changeme123
```

### Prometheus Queries

```bash
# Access Prometheus
kubectl port-forward svc/prometheus 9090:9090 --namespace monitoring

# Open browser to http://localhost:9090
```

## Backup & Disaster Recovery

### Database Backups

```bash
# Daily backup script
kubectl exec -it deployment/postgres --namespace phase-5 -- \
  pg_dump -U user dbname > backup-$(date +%Y-%m-%d).sql

# Upload to S3
aws s3 cp backup-$(date +%Y-%m-%d).sql s3://backups/db/
```

### Kubernetes Resource Backup

```bash
# Install Velero
kubectl apply -f https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz

# Create backup
velero backup create daily-backup --namespace phase-5

# Schedule backups
velero schedule create daily-backup --schedule="0 2 * * *" --namespace phase-5
```

## Security

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: phase-5
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Pod Security Policies

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-backend
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: backend
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

## Troubleshooting

### Check Pod Status

```bash
kubectl describe pod <pod-name> --namespace phase-5
kubectl logs <pod-name> --namespace phase-5
kubectl logs -f <pod-name> --namespace phase-5
```

### Check Services

```bash
kubectl get endpoints --namespace phase-5
kubectl describe service <service-name> --namespace phase-5
```

### Check Dapr Sidecar

```bash
kubectl logs <pod-name> -c daprd --namespace phase-5
```

### Common Issues

1. **Pods Not Starting**: Check resource limits, image availability
2. **High Latency**: Check database connections, Kafka lag
3. **WebSocket Disconnects**: Check load balancer timeout settings
4. **AI Requests Failing**: Check Ollama service availability

## Rollback

```bash
# Helm rollback
helm rollback backend 1 --namespace phase-5

# Kubernetes rollout
kubectl rollout undo deployment/backend --namespace phase-5
```

## Performance Tuning

### Database Connection Pool

```python
# In backend config
SQLALCHEMY_DATABASE_URI = "postgresql://..."
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 40,
    "pool_timeout": 30,
    "pool_recycle": 3600
}
```

### Kafka Consumer Settings

```yaml
# In Dapr component
consumer:
  autoCommitIntervalMs: 5000
  heartbeatIntervalMs: 3000
  maxProcessingMessages: 10
```

## Maintenance Windows

### Zero-Downtime Deployment

```bash
# Kubernetes does rolling updates automatically
kubectl set image deployment/backend backend=backend:v2.0 --namespace phase-5

# Monitor rollout
kubectl rollout status deployment/backend --namespace phase-5
```

## Cost Optimization

- Use spot instances for non-critical workloads
- Right-size resources based on metrics
- Enable cluster autoscaler
- Use reserved instances for baseline load

## Support & Escalation

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical | 15 minutes | On-call engineer |
| High | 1 hour | Tech lead |
| Medium | 4 hours | Team lead |
| Low | 1 business day | Sprint planning |

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Dapr Documentation](https://dapr.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
