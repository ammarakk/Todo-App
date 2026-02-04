#!/bin/bash
# Final Verification Script for Phase 5
# Verifies all components are properly configured and deployed
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 5 Final Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

FAILURES=0
WARNINGS=0

# 1. Check Kubernetes cluster connectivity
echo -e "${YELLOW}1. Checking Kubernetes cluster...${NC}"

if kubectl cluster-info > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Kubernetes cluster is accessible${NC}"
  echo "  Cluster: $(kubectl config current-context)"
else
  echo -e "${RED}✗ Cannot connect to Kubernetes cluster${NC}"
  FAILURES=$((FAILURES + 1))
fi

# 2. Check namespace
echo ""
echo -e "${YELLOW}2. Checking namespace...${NC}"

if kubectl get namespace phase-5 > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Namespace 'phase-5' exists${NC}"
else
  echo -e "${YELLOW}⚠ Namespace 'phase-5' not found${NC}"
  echo "  Run: kubectl create namespace phase-5"
  WARNINGS=$((WARNINGS + 1))
fi

# 3. Check deployments
echo ""
echo -e "${YELLOW}3. Checking deployments...${NC}"

DEPLOYMENTS=("backend" "notification" "postgres")
for deployment in "${DEPLOYMENTS[@]}"; do
  if kubectl get deployment "$deployment" -n phase-5 > /dev/null 2>&1; then
    READY_REPLICAS=$(kubectl get deployment "$deployment" -n phase-5 -o jsonpath='{.status.readyReplicas}')
    DESIRED_REPLICAS=$(kubectl get deployment "$deployment" -n phase-5 -o jsonpath='{.spec.replicas}')

    if [ "$READY_REPLICAS" == "$DESIRED_REPLICAS" ]; then
      echo -e "${GREEN}✓ Deployment '$deployment' is ready (${READY_REPLICAS}/${DESIRED_REPLICAS})${NC}"
    else
      echo -e "${YELLOW}⚠ Deployment '$deployment' not ready (${READY_REPLICAS}/${DESIRED_REPLICAS})${NC}"
      WARNINGS=$((WARNINGS + 1))
    fi
  else
    echo -e "${RED}✗ Deployment '$deployment' not found${NC}"
    FAILURES=$((FAILURES + 1))
  fi
done

# 4. Check pods
echo ""
echo -e "${YELLOW}4. Checking pods...${NC}"

PODS=$(kubectl get pods -n phase-5 --no-headers 2>/dev/null | wc -l)
RUNNING=$(kubectl get pods -n phase-5 --no-headers 2>/dev/null | grep "Running" | wc -l)

if [ "$PODS" -gt 0 ]; then
  echo -e "${GREEN}✓ Found ${PODS} pods (${RUNNING} running)${NC}"

  # Check for failing pods
  FAILED=$(kubectl get pods -n phase-5 --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l)
  if [ "$FAILED" -gt 0 ]; then
    echo -e "${YELLOW}⚠ ${FAILED} pods are not running${NC}"
    kubectl get pods -n phase-5 | grep -v "Running\|Completed"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo -e "${YELLOW}⚠ No pods found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# 5. Check services
echo ""
echo -e "${YELLOW}5. Checking services...${NC}"

SERVICES=("backend-service" "notification-service" "postgres")
for service in "${SERVICES[@]}"; do
  if kubectl get service "$service" -n phase-5 > /dev/null 2>&1; then
    TYPE=$(kubectl get service "$service" -n phase-5 -o jsonpath='{.spec.type}')
    echo -e "${GREEN}✓ Service '$service' exists (${TYPE})${NC}"
  else
    echo -e "${YELLOW}⚠ Service '$service' not found${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
done

# 6. Check ingress
echo ""
echo -e "${YELLOW}6. Checking ingress...${NC}"

INGRESS=$(kubectl get ingress -n phase-5 --no-headers 2>/dev/null | wc -l)
if [ "$INGRESS" -gt 0 ]; then
  echo -e "${GREEN}✓ Found ${INGRESS} ingress resources${NC}"

  # Check TLS configuration
  TLS_INGRESS=$(kubectl get ingress -n phase-5 -o json | jq '.items[] | select(.spec.tls != null) | .metadata.name' | wc -l)
  if [ "$TLS_INGRESS" -gt 0 ]; then
    echo -e "${GREEN}✓ ${TLS_INGRESS} ingress resources have TLS configured${NC}"
  else
    echo -e "${YELLOW}⚠ No TLS configured on ingress${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo -e "${YELLOW}⚠ No ingress resources found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# 7. Check certificates
echo ""
echo -e "${YELLOW}7. Checking TLS certificates...${NC}"

if kubectl get certificates -n phase-5 > /dev/null 2>&1; then
  CERTS=$(kubectl get certificates -n phase-5 --no-headers | wc -l)
  echo -e "${GREEN}✓ Found ${CERTS} certificates${NC}"

  # Check certificate status
  READY_CERTS=$(kubectl get certificates -n phase-5 -o json | jq '.items[] | select(.status.conditions[].status == "True") | .metadata.name' | wc -l)
  if [ "$READY_CERTS" -eq "$CERTS" ]; then
    echo -e "${GREEN}✓ All certificates are ready${NC}"
  else
    echo -e "${YELLOW}⚠ Some certificates are not ready${NC}"
    kubectl get certificates -n phase-5
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo -e "${YELLOW}⚠ No certificates found (cert-manager may not be installed)${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# 8. Check HPA
echo ""
echo -e "${YELLOW}8. checking Horizontal Pod Autoscalers...${NC}"

if kubectl get hpa -n phase-5 > /dev/null 2>&1; then
  HPA_COUNT=$(kubectl get hpa -n phase-5 --no-headers | wc -l)
  echo -e "${GREEN}✓ Found ${HPA_COUNT} HPA resources${NC}"
  kubectl get hpa -n phase-5
else
  echo -e "${YELLOW}⚠ No HPA resources found${NC}"
  echo "  Run: kubectl apply -f k8s/autoscaler.yaml"
  WARNINGS=$((WARNINGS + 1))
fi

# 9. Check secrets
echo ""
echo -e "${YELLOW}9. Checking secrets...${NC}"

SECRETS=("db-credentials" "ollama-config")
for secret in "${SECRETS[@]}"; do
  if kubectl get secret "$secret" -n phase-5 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Secret '$secret' exists${NC}"
  else
    echo -e "${RED}✗ Secret '$secret' not found${NC}"
    echo "  Run: kubectl create secret generic $secret --from-literal=..."
    FAILURES=$((FAILURES + 1))
  fi
done

# 10. Check monitoring
echo ""
echo -e "${YELLOW}10. Checking monitoring stack...${NC}"

# Check Prometheus
if kubectl get svc prometheus-kube-prometheus-prometheus -n monitoring > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Prometheus is running${NC}"
else
  echo -e "${YELLOW}⚠ Prometheus not found in monitoring namespace${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Check Grafana
if kubectl get svc grafana -n monitoring > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Grafana is running${NC}"
else
  echo -e "${YELLOW}⚠ Grafana not found in monitoring namespace${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# 11. Check Dapr
echo ""
echo -e "${YELLOW}11. Checking Dapr sidecars...${NC}"

DAPR_PODS=$(kubectl get pods -n phase-5 -o json | jq '.items[] | select(.spec.containers[].name == "daprd") | .metadata.name' | wc -l)
if [ "$DAPR_PODS" -gt 0 ]; then
  echo -e "${GREEN}✓ Dapr sidecars are injected (${DAPR_PODS} pods)${NC}"
else
  echo -e "${YELLOW}⚠ Dapr sidecars not found${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# 12. Run health check
echo ""
echo -e "${YELLOW}12. Running health check...${NC}"

# Port forward to backend
BACKEND_POD=$(kubectl get pod -n phase-5 -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$BACKEND_POD" ]; then
  echo "  Forwarding port to pod: ${BACKEND_POD}"

  # Start port forward in background
  kubectl port-forward -n phase-5 pod/$BACKEND_POD 8000:8000 > /dev/null 2>&1 &
  PF_PID=$!

  # Wait for port forward to be ready
  sleep 3

  # Run health check
  if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
  else
    echo -e "${RED}✗ Backend health check failed${NC}"
    FAILURES=$((FAILURES + 1))
  fi

  # Kill port forward
  kill $PF_PID 2>/dev/null
else
  echo -e "${YELLOW}⚠ Could not find backend pod${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $FAILURES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed! System is ready for production.${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Configure DNS records for your domain"
  echo "  2. Verify SSL certificates are issued"
  echo "  3. Run security scan: ./scripts/security-scan.sh"
  echo "  4. Run performance tests: ./scripts/performance-test.sh"
  echo "  5. Monitor Grafana dashboards"
  exit 0
elif [ $FAILURES -eq 0 ]; then
  echo -e "${YELLOW}⚠ System is operational with ${WARNINGS} warnings${NC}"
  echo "  Review warnings above and address if needed"
  exit 0
else
  echo -e "${RED}✗ Found ${FAILURES} failures and ${WARNINGS} warnings${NC}"
  echo "  Please address the failures before deploying to production"
  exit 1
fi
