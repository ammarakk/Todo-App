#!/bin/bash
# Security Hardening Verification Script
# Verifies no hardcoded secrets, TLS is configured, and input validation is in place
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Security Hardening Verification${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

ISSUES_FOUND=0

# 1. Check for hardcoded secrets
echo -e "${YELLOW}1. Checking for hardcoded secrets...${NC}"

SECRETS_FOUND=$(grep -r "password\|api_key\|secret\|token" backend/src/ \
  --exclude-dir=__pycache__ \
  --include="*.py" \
  | grep -v "os.getenv\|environ\|Secret\|Validation\|#" \
  || true)

if [ -n "$SECRETS_FOUND" ]; then
  echo -e "${RED}✗ Found hardcoded secrets:${NC}"
  echo "$SECRETS_FOUND"
  ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
  echo -e "${GREEN}✓ No hardcoded secrets found${NC}"
fi

# 2. Check for Kubernetes Secrets usage
echo ""
echo -e "${YELLOW}2. Checking Kubernetes Secrets usage...${NC}"

if kubectl get secrets -n phase-5 > /dev/null 2>&1; then
  SECRETS_COUNT=$(kubectl get secrets -n phase-5 --no-headers | wc -l)

  if [ "$SECRETS_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Found ${SECRETS_COUNT} Kubernetes secrets${NC}"

    # Verify important secrets exist
    IMPORTANT_SECRETS=("db-credentials" "ollama-config" "sendgrid-config")
    for secret in "${IMPORTANT_SECRETS[@]}"; do
      if kubectl get secret "$secret" -n phase-5 > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Secret '$secret' exists${NC}"
      else
        echo -e "${YELLOW}  ⚠ Secret '$secret' not found${NC}"
      fi
    done
  else
    echo -e "${RED}✗ No Kubernetes secrets found${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
  fi
else
  echo -e "${YELLOW}⚠ Kubernetes cluster not accessible${NC}"
fi

# 3. Check TLS certificates
echo ""
echo -e "${YELLOW}3. Checking TLS certificates...${NC}"

if kubectl get certificates -n phase-5 > /dev/null 2>&1; then
  CERTS=$(kubectl get certificates -n phase-5 --no-headers | wc -l)

  if [ "$CERTS" -gt 0 ]; then
    echo -e "${GREEN}✓ Found ${CERTS} TLS certificates${NC}"

    # Check certificate status
    kubectl get certificates -n phase-5 | while read name ready secret age; do
      if [ "$ready" == "True" ]; then
        echo -e "${GREEN}  ✓ Certificate '$name' is ready${NC}"
      else
        echo -e "${RED}  ✗ Certificate '$name' is not ready${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
      fi
    done
  else
    echo -e "${RED}✗ No TLS certificates found${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
  fi
else
  echo -e "${YELLOW}⚠ Kubernetes cluster not accessible${NC}"
fi

# 4. Check NetworkPolicies
echo ""
echo -e "${YELLOW}4. Checking NetworkPolicies...${NC}"

if kubectl get networkpolicies -n phase-5 > /dev/null 2>&1; then
  NETPOL_COUNT=$(kubectl get networkpolicies -n phase-5 --no-headers | wc -l)

  if [ "$NETPOL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Found ${NETPOL_COUNT} NetworkPolicies${NC}"
  else
    echo -e "${YELLOW}⚠ No NetworkPolicies found (recommended for security)${NC}"
  fi
else
  echo -e "${YELLOW}⚠ Kubernetes cluster not accessible${NC}"
fi

# 5. Check input validation in API
echo ""
echo -e "${YELLOW}5. Checking input validation...${NC}"

VALIDATION_FILES=$(find backend/src/api -name "*.py" -exec grep -l "pydantic\|BaseModel\|Field\|validator" {} \;)

if [ -n "$VALIDATION_FILES" ]; then
  echo -e "${GREEN}✓ Input validation found in:${NC}"
  echo "$VALIDATION_FILES" | while read file; do
    echo "  - $file"
  done
else
  echo -e "${RED}✗ No input validation found${NC}"
  ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 6. Check for SQL injection protection
echo ""
echo -e "${YELLOW}6. Checking SQL injection protection...${NC}"

if grep -r "execute\|executemany" backend/src/ --include="*.py" | grep -v "session.execute\|text(" > /dev/null 2>&1; then
  echo -e "${YELLOW}⚠ Found raw SQL execution - ensure parameters are used${NC}"
else
  echo -e "${GREEN}✓ Using SQLAlchemy ORM (SQL injection protected)${NC}"
fi

# 7. Check for CORS configuration
echo ""
echo -e "${YELLOW}7. Checking CORS configuration...${NC}"

if grep -r "CORSMiddleware\|allow_origins" backend/src/main.py > /dev/null 2>&1; then
  echo -e "${GREEN}✓ CORS is configured${NC}"

  # Check if CORS is restrictive
  if grep -r "allow_origins.*\*" backend/src/main.py > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ CORS allows all origins (*) - consider restricting${NC}"
  fi
else
  echo -e "${RED}✗ CORS not configured${NC}"
  ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 8. Check for rate limiting
echo ""
echo -e "${YELLOW}8. Checking rate limiting...${NC}"

if grep -r "rate_limit\|RateLimiter\|slowapi" backend/src/ > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Rate limiting is configured${NC}"
else
  echo -e "${YELLOW}⚠ No rate limiting found (consider implementing)${NC}"
fi

# 9. Check for security headers
echo ""
echo -e "${YELLOW}9. Checking security headers...${NC}"

if grep -r "X-Content-Type\|X-Frame\|CSP\|Strict-Transport" backend/src/ > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Security headers are configured${NC}"
else
  echo -e "${YELLOW}⚠ Security headers not found (consider adding)${NC}"
fi

# 10. Check for dependency vulnerabilities
echo ""
echo -e "${YELLOW}10. Checking for dependency vulnerabilities...${NC}"

if command -v safety &> /dev/null; then
  cd backend
  if safety check --json > /tmp/safety-report.json 2>&1; then
    echo -e "${GREEN}✓ No known vulnerabilities found${NC}"
  else
    echo -e "${RED}✗ Vulnerabilities found:${NC}"
    cat /tmp/safety-report.json
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
  fi
  cd ..
else
  echo -e "${YELLOW}⚠ 'safety' not installed - run: pip install safety${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Security Scan Summary${NC}"
echo -e "${GREEN}========================================${NC}"

if [ $ISSUES_FOUND -eq 0 ]; then
  echo -e "${GREEN}✓ All security checks passed!${NC}"
  exit 0
else
  echo -e "${RED}✗ Found ${ISSUES_FOUND} issues that need attention${NC}"
  exit 1
fi
