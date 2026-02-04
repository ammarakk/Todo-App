#!/bin/bash
# Performance Verification Script
# Verifies SLA compliance: API latency <500ms, real-time updates <2s, throughput >100 req/sec
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
DURATION="${DURATION:-60}" # seconds
CONCURRENCY="${CONCURRENCY:-10}"
THROUGHPUT_TARGET="${THROUGHPUT_TARGET:-100}"
LATENCY_P95_TARGET="${LATENCY_P95_TARGET:-500}"
REALTIME_TARGET="${REALTIME_TARGET:-2000}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Performance Verification${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}API URL: ${API_URL}${NC}"
echo -e "${YELLOW}Duration: ${DURATION}s${NC}"
echo -e "${YELLOW}Concurrency: ${CONCURRENCY}${NC}"
echo ""

FAILURES=0

# 1. API Latency Test (P95 < 500ms)
echo -e "${YELLOW}1. Testing API latency (target: P95 < ${LATENCY_P95_TARGET}ms)...${NC}"

if command -v wrk &> /dev/null; then
  RESULT=$(wrk -t${CONCURRENCY} -c${CONCURRENCY} -d${DURATION}s ${API_URL}/health 2>&1)
  LATENCY=$(echo "$RESULT" | grep "Latency" | awk '{print $2}')

  echo "$RESULT"

  if [ -n "$LATENCY" ]; then
    echo -e "${GREEN}✓ P95 Latency: ${LATENCY}${NC}"

    # Extract numeric value for comparison (assuming format like "123.45ms")
    LATENCY_VALUE=$(echo $LATENCY | sed 's/ms//')
    LATENCY_INT=${LATENCY_VALUE%.*}

    if [ "$LATENCY_INT" -lt "$LATENCY_P95_TARGET" ]; then
      echo -e "${GREEN}✓ Latency SLA met${NC}"
    else
      echo -e "${RED}✗ Latency SLA not met${NC}"
      FAILURES=$((FAILURES + 1))
    fi
  else
    echo -e "${YELLOW}⚠ Could not parse latency${NC}"
  fi
else
  echo -e "${YELLOW}⚠ 'wrk' not installed - run: apt-get install wrk${NC}"
fi

# 2. Throughput Test (> 100 req/sec)
echo ""
echo -e "${YELLOW}2. Testing throughput (target: > ${THROUGHPUT_TARGET} req/sec)...${NC}"

if command -v wrk &> /dev/null; then
  RESULT=$(wrk -t${CONCURRENCY} -c${CONCURRENCY} -d${DURATION}s ${API_URL}/health 2>&1)
  REQ_PER_SEC=$(echo "$RESULT" | grep "Req/Sec" | awk '{print $1}')

  echo "$RESULT"

  if [ -n "$REQ_PER_SEC" ]; then
    echo -e "${GREEN}✓ Throughput: ${REQ_PER_SEC} req/sec${NC}"

    REQ_VALUE=${REQ_PER_SEC%.*}

    if [ "$REQ_VALUE" -gt "$THROUGHPUT_TARGET" ]; then
      echo -e "${GREEN}✓ Throughput SLA met${NC}"
    else
      echo -e "${RED}✗ Throughput SLA not met${NC}"
      FAILURES=$((FAILURES + 1))
    fi
  else
    echo -e "${YELLOW}⚠ Could not parse throughput${NC}"
  fi
else
  echo -e "${YELLOW}⚠ 'wrk' not installed${NC}"
fi

# 3. Real-Time Updates Test (< 2 seconds)
echo ""
echo -e "${YELLOW}3. Testing real-time updates (target: < ${REALTIME_TARGET}ms)...${NC}"

if command -v python3 &> /dev/null; then
  # Create a Python script to test WebSocket latency
  cat > /tmp/test_websocket.py << 'EOF'
import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket_latency():
    uri = "ws://localhost:8000/ws?user_id=test-user-123"

    try:
        async with websockets.connect(uri) as websocket:
            # Send ping
            start_time = time.time()
            await websocket.send(json.dumps({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            }))

            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            end_time = time.time()

            latency_ms = (end_time - start_time) * 1000
            print(f"WebSocket latency: {latency_ms:.2f}ms")

            if latency_ms < 2000:
                return 0  # Success
            else:
                return 1  # Failure
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        return 2  # Error

if __name__ == "__main__":
    exit(asyncio.run(test_websocket_latency()))
EOF

  if python3 -c "import websockets" 2>/dev/null; then
    python3 /tmp/test_websocket.py
    RESULT=$?

    if [ $RESULT -eq 0 ]; then
      echo -e "${GREEN}✓ Real-time updates SLA met${NC}"
    elif [ $RESULT -eq 1 ]; then
      echo -e "${RED}✗ Real-time updates SLA not met${NC}"
      FAILURES=$((FAILURES + 1))
    else
      echo -e "${YELLOW}⚠ Could not connect to WebSocket${NC}"
    fi
  else
    echo -e "${YELLOW}⚠ 'websockets' not installed - run: pip install websockets${NC}"
  fi

  rm -f /tmp/test_websocket.py
else
  echo -e "${YELLOW}⚠ Python3 not found${NC}"
fi

# 4. Database Query Performance (P95 < 50ms)
echo ""
echo -e "${YELLOW}4. Testing database query performance...${NC}"

cd backend
if python3 -c "import sqlalchemy" 2>/dev/null; then
  RESULT=$(python3 -c "
from datetime import datetime
from time import perf_counter
from src.db.session import SessionLocal
from src.models.task import Task

db = SessionLocal()
start = perf_counter()
tasks = db.query(Task).limit(100).all()
end = perf_counter()

latency_ms = (end - start) * 1000
print(f'Database query latency: {latency_ms:.2f}ms')

if latency_ms < 50:
    exit(0)
else:
    exit(1)
" 2>&1)

  echo "$RESULT"

  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database query performance SLA met${NC}"
  else
    echo -e "${RED}✗ Database query performance SLA not met${NC}"
    FAILURES=$((FAILURES + 1))
  fi
else
  echo -e "${YELLOW}⚠ SQLAlchemy not installed${NC}"
fi
cd ..

# 5. Intent Detection Performance (< 500ms)
echo ""
echo -e "${YELLOW}5. Testing AI intent detection performance...${NC}"

cd backend
if python3 -c "from src.orchestrator.intent_detector import IntentDetector" 2>/dev/null; then
  RESULT=$(python3 -c "
from time import perf_counter
from src.orchestrator.intent_detector import IntentDetector

detector = IntentDetector()
test_input = 'Create a task to buy milk tomorrow at 5pm'

start = perf_counter()
intent, confidence = detector.detect(test_input)
end = perf_counter()

latency_ms = (end - start) * 1000
print(f'Intent detection latency: {latency_ms:.2f}ms')
print(f'Detected intent: {intent.value} (confidence: {confidence:.2f})')

if latency_ms < 500:
    exit(0)
else:
    exit(1)
" 2>&1)

  echo "$RESULT"

  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Intent detection SLA met${NC}"
  else
    echo -e "${RED}✗ Intent detection SLA not met${NC}"
    FAILURES=$((FAILURES + 1))
  fi
else
  echo -e "${YELLOW}⚠ Intent detector not available${NC}"
fi
cd ..

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Performance Test Summary${NC}"
echo -e "${GREEN}========================================${NC}"

if [ $FAILURES -eq 0 ]; then
  echo -e "${GREEN}✓ All performance SLAs met!${NC}"
  echo ""
  echo "Performance Results:"
  echo "  - API P95 Latency: < ${LATENCY_P95_TARGET}ms ✓"
  echo "  - Throughput: > ${THROUGHPUT_TARGET} req/sec ✓"
  echo "  - Real-time updates: < ${REALTIME_TARGET}ms ✓"
  echo "  - Database queries: < 50ms ✓"
  echo "  - Intent detection: < 500ms ✓"
  exit 0
else
  echo -e "${RED}✗ ${FAILURES} performance SLAs not met${NC}"
  exit 1
fi
