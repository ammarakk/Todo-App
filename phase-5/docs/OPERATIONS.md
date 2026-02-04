# Phase 5 Operations Runbook

**Version**: 1.0
**Last Updated**: 2026-02-04
**Purpose**: Operational procedures for Phase 5 Todo Application

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Alerting & On-Call](#alerting--on-call)
3. [Incident Response](#incident-response)
4. [Common Issues & Solutions](#common-issues--solutions)
5. [Maintenance Procedures](#maintenance-procedures)
6. [Performance Tuning](#performance-tuning)
7. [Capacity Planning](#capacity-planning)
8. [Disaster Recovery](#disaster-recovery)

---

## Daily Operations

### Morning Checklist (Daily 9 AM)

- [ ] Check Grafana dashboards for anomalies
- [ ] Verify all pods are running
- [ ] Check error rates in Prometheus
- [ ] Review overnight alerts
- [ ] Verify backups completed successfully

**Commands**:
```bash
# Check pod health
kubectl get pods -n phase-5

# Check backup jobs
kubectl get cronjobs -n phase-5
kubectl logs -l job-name=database-backup -n phase-5 --tail=-1

# Check system metrics
kubectl top pods -n phase-5
kubectl top nodes
```

### Weekly Review (Friday 4 PM)

- [ ] Review weekly performance metrics
- [ ] Check SSL certificate expiry
- [ ] Review and rotate secrets (if needed)
- [ ] Clean up old backups
- [ ] Review and update runbook

**Commands**:
```bash
# Check certificate expiry
kubectl get certificates -n phase-5
kubectl describe certificate backend-api-tls -n phase-5 | grep "Not After"

# Clean up old backups (keep last 30 days)
aws s3 ls s3://todo-app-backups/snapshots/ | \
  awk '{print $4}' | \
  head -n -30 | \
  xargs -I {} aws s3 rm s3://todo-app-backups/snapshots/{}
```

---

## Alerting & On-Call

### Alert Severity Levels

| Severity | Response Time | Escalation | Examples |
|----------|---------------|------------|----------|
| **P1 - Critical** | 15 minutes | 30 min | Complete service outage, data loss |
| **P2 - High** | 1 hour | 2 hours | Service degradation, high error rate |
| **P3 - Medium** | 4 hours | Next business day | Performance issues, minor bugs |
| **P4 - Low** | 1 week | N/A | Documentation, cosmetic issues |

### Common Alerts

#### 1. HighErrorRate (P1)
**Trigger**: Error rate > 5% for 5 minutes

**Investigation**:
```bash
# Check error rate in Prometheus
open http://localhost:9090/graph?g0 expr=rate(http_requests_total{status="error"}[5m])

# View recent logs
kubectl logs -l app=backend -n phase-5 --tail=100

# Check pod status
kubectl get pods -n phase-5
```

**Resolution**:
- Identify failing component from logs
- Check database connectivity
- Verify external services (Kafka, Ollama)
- Rollback if recent deployment caused issues

#### 2. HighLatency (P2)
**Trigger**: P95 latency > 3 seconds for 5 minutes

**Investigation**:
```bash
# Check latency metrics
open http://localhost:9090/graph?g0.expr=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Check database query performance
kubectl logs -l app=backend -n phase-5 | grep "slow query"

# Check resource utilization
kubectl top pods -n phase-5
```

**Resolution**:
- Scale up pods if CPU/memory constrained
- Optimize slow database queries
- Restart stuck pods
- Enable caching for frequently accessed data

#### 3. PodCrashLooping (P1)
**Trigger**: Pod restart count > 5 in 10 minutes

**Investigation**:
```bash
# Check pod status
kubectl get pods -n phase-5

# Describe pod
kubectl describe pod <pod-name> -n phase-5

# View logs
kubectl logs <pod-name> -n phase-5 --previous
```

**Resolution**:
- Check logs for error messages
- Verify secrets and configuration
- Check resource limits
- Restart deployment if needed

#### 4. DatabaseConnectionFailed (P1)
**Trigger**: Cannot connect to database

**Investigation**:
```bash
# Check PostgreSQL pod
kubectl get pods -n phase-5 -l app=postgres

# Test connection
kubectl exec -it <backend-pod> -n phase-5 -- psql ${DATABASE_URL}

# Check database credentials
kubectl describe secret db-credentials -n phase-5
```

**Resolution**:
- Verify database pod is running
- Check network policies
- Rotate credentials if compromised
- Restart backend pods after fixing

---

## Incident Response

### Incident Lifecycle

1. **Detection** - Alert triggered
2. **Acknowledgement** - On-call engineer acknowledges
3. **Investigation** - Gather diagnostic information
4. **Mitigation** - Apply workaround or fix
5. **Resolution** - Verify service is restored
6. **Post-Mortem** - Document incident and improvements

### Incident Commands

**Create Incident Channel**:
```bash
# Create Slack channel
/slack create channel #incident-$(date +%Y%m%d)

# Set topic
/slack set topic "P1 - High Error Rate - Investigating"
```

**Declare Incident**:
```bash
# Post to team
echo "🚨 INCIDENT DECLARED: High Error Rate
Severity: P1
Time: $(date)
Lead: @on-call
Channel: #incident-$(date +%Y%m%d)
Status: Investigating" | slack post
```

**Update Incident**:
```bash
# Update status
/slack post "UPDATE: Identified issue in database connection pool. Working on fix."
```

**Close Incident**:
```bash
/slack post "RESOLVED: Error rate back to normal. Post-mortem to follow."
```

### Major Incident Template

```markdown
# Major Incident Report

**Date**: YYYY-MM-DD
**Incident ID**: INC-YYYY-MM
**Severity**: P1/P2/P3
**Duration**: X hours
**Impact**: Y users affected

## Summary
Brief description of what happened

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix applied
- HH:MM - Service restored

## Root Cause
Technical root cause analysis

## Resolution
What was done to fix it

## Prevention
What will be done to prevent recurrence

## Action Items
- [ ] Action item 1
- [ ] Action item 2
```

---

## Common Issues & Solutions

### Issue: API Returns 500 Errors

**Symptoms**:
- API endpoints returning 500 status codes
- Logs show database connection errors

**Diagnosis**:
```bash
# Check backend logs
kubectl logs -l app=backend -n phase-5 --tail=50

# Check database connectivity
kubectl exec -it <backend-pod> -n phase-5 -- pgsql ${DATABASE_URL}
```

**Solutions**:
1. Restart backend pods
   ```bash
   kubectl rollout restart deployment/backend -n phase-5
   ```

2. Check database credentials
   ```bash
   kubectl describe secret db-credentials -n phase-5
   ```

3. Scale database if needed
   ```bash
   kubectl patch postgresql postgres -n phase-5 --type='json' \
     -p='[{"op": "replace", "path": "/spec/resources/limits/memory", "value":"2Gi"}]'
   ```

### Issue: WebSocket Connections Dropping

**Symptoms**:
- Clients disconnected frequently
- WebSocket errors in logs

**Diagnosis**:
```bash
# Check WebSocket connections
kubectl logs -l app=backend -n phase-5 | grep -i websocket

# Check ingress timeout
kubectl describe ingress websocket-ingress -n phase-5
```

**Solutions**:
1. Increase ingress timeout
   ```yaml
   nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
   nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
   ```

2. Enable WebSocket keep-alive
   ```yaml
   nginx.ingress.kubernetes.io/proxy-http-version: "1.1"
   nginx.ingress.kubernetes.io/enable-websocket: "true"
   ```

### Issue: Reminders Not Sending

**Symptoms**:
- Reminders scheduled but not delivered
- No email notifications received

**Diagnosis**:
```bash
# Check notification service logs
kubectl logs -l app=notification -n phase-5

# Check reminder scheduler logs
kubectl logs -l app=backend -c reminder-scheduler -n phase-5

# Check Kafka topic
docker exec redpanda-1 rpk topic consume reminders -n 10
```

**Solutions**:
1. Restart notification service
   ```bash
   kubectl rollout restart deployment/notification -n phase-5
   ```

2. Verify SendGrid credentials
   ```bash
   kubectl describe secret sendgrid-config -n phase-5
   ```

3. Check Kafka connectivity
   ```bash
   kubectl exec -it <backend-pod> -n phase-5 -- nc -zv kafka 9092
   ```

### Issue: High CPU/Memory Usage

**Symptoms**:
- Pods running out of resources
- OOMKilled errors

**Diagnosis**:
```bash
# Check resource usage
kubectl top pods -n phase-5
kubectl describe pod <pod-name> -n phase-5 | grep -A 5 "Limits"
```

**Solutions**:
1. Adjust resource limits
   ```bash
   kubectl set resources deployment/backend \
     --limits=cpu=2000m,memory=2Gi \
     --requests=cpu=500m,memory=512Mi \
     -n phase-5
   ```

2. Enable HPA
   ```bash
   kubectl apply -f k8s/autoscaler.yaml
   ```

3. Profile application for memory leaks
   ```bash
   kubectl exec -it <backend-pod> -n phase-5 -- python -m memory_profiler src/main.py
   ```

---

## Maintenance Procedures

### Rolling Update

```bash
# Update image
kubectl set image deployment/backend \
  backend=YOUR_REGISTRY/todo-app-backend:v2.0 \
  -n phase-5

# Watch rollout status
kubectl rollout status deployment/backend -n phase-5

# If issues occur, rollback
kubectl rollout undo deployment/backend -n phase-5
```

### Database Migration

```bash
# Get backend pod
BACKEND_POD=$(kubectl get pod -n phase-5 -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migration script
kubectl exec -n phase-5 ${BACKEND_POD} -- python scripts/migrate.py

# Verify migration
kubectl exec -n phase-5 ${BACKEND_POD} -- python scripts/verify_migration.py
```

### Secret Rotation

```bash
# 1. Generate new secret
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update secret
kubectl create secret generic db-credentials-new \
  --from-literal=username=postgres \
  --from-literal=password=${NEW_PASSWORD} \
  --from-literal=host=postgres.postgres.svc.cluster.local \
  -n phase-5

# 3. Update deployment to use new secret
kubectl set env deployment/backend \
  --from=secret/db-credentials-new \
  -n phase-5

# 4. Rollout restart
kubectl rollout restart deployment/backend -n phase-5

# 5. Delete old secret
kubectl delete secret db-credentials -n phase-5
kubectl rename secret/db-credentials-new db-credentials -n phase-5
```

---

## Performance Tuning

### Database Optimization

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Create indexes
CREATE INDEX idx_tasks_user_id_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 'xxx' AND status = 'active';
```

### API Caching

```python
# Enable Redis caching (if using Redis)
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_tasks(user_id: str):
    # Cached implementation
    pass
```

### Connection Pooling

```python
# Adjust database pool size in config.py
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
```

---

## Capacity Planning

### Scaling Metrics

**Current Capacity**:
- Backend: 3-10 pods (via HPA)
- Database: 1 pod (can scale vertically)
- Kafka: 3 brokers, 6 partitions

**When to Scale**:
- CPU > 70% for 5 minutes → Scale up
- Memory > 80% for 5 minutes → Scale up
- Request rate > 100 req/sec/pod → Scale up

**Quarterly Review**:
- Analyze growth trends
- Plan capacity upgrades
- Budget for additional resources

---

## Disaster Recovery

### RTO & RPO Targets

| Service | Recovery Time Objective (RTO) | Recovery Point Objective (RPO) |
|---------|-------------------------------|-------------------------------|
| Backend API | 15 minutes | 5 minutes |
| Database | 1 hour | 15 minutes |
| Kafka | 30 minutes | 10 minutes |

### Recovery Procedures

**1. Restore from Backup**:
```bash
./scripts/backup-database.sh restore todo-app-backup-20260204_020000.sql.gz
```

**2. Failover to Backup Region**:
```bash
# Update DNS to point to backup region
# Deploy backup stack
kubectl apply -f k8s/backup-region/

# Verify failover
curl https://backup.todo-app.com/health
```

**3. Full Disaster Recovery**:
```bash
# 1. Provision new cluster
# 2. Install dependencies (Dapr, Kafka, etc.)
# 3. Deploy from Helm charts
# 4. Restore database from backup
# 5. Update DNS to new cluster
# 6. Verify all services
```

---

## Contact Information

- **On-Call**: +1-XXX-XXX-XXXX (PagerDuty)
- **Slack**: #todo-app-ops
- **Email**: ops@yourdomain.com
- **GitHub**: https://github.com/your-org/todo-app/issues

---

**Last Updated**: 2026-02-04
**Version**: 1.0
**Maintained By**: DevOps Team
