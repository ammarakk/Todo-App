#!/bin/bash
# Test Runner Script for Phase 5 Backend
# Runs different test suites with proper flags

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Phase 5 Backend Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Default behavior
COVERAGE_FLAG="--cov=src --cov-report=html --cov-report=term-missing"
VERBOSE_FLAG="-v"
MARKER=""

# Parse arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
  unit)
    echo -e "${YELLOW}Running Unit Tests...${NC}"
    MARKER="-m unit"
    ;;
  integration)
    echo -e "${YELLOW}Running Integration Tests...${NC}"
    MARKER="-m integration"
    ;;
  contract)
    echo -e "${YELLOW}Running Contract Tests...${NC}"
    MARKER="-m contract"
    ;;
  e2e)
    echo -e "${YELLOW}Running End-to-End Tests...${NC}"
    MARKER="-m e2e"
    ;;
  performance)
    echo -e "${YELLOW}Running Performance Tests...${NC}"
    MARKER="-m performance"
    COVERAGE_FLAG=""  # No coverage for performance tests
    ;;
  fast)
    echo -e "${YELLOW}Running Fast Tests (Unit + Contract)...${NC}"
    MARKER="-m 'not slow'"
    ;;
  all)
    echo -e "${YELLOW}Running All Tests...${NC}"
    MARKER=""
    ;;
  *)
    echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
    echo "Usage: ./run_tests.sh [unit|integration|contract|e2e|performance|fast|all]"
    exit 1
    ;;
esac

echo ""
echo "Command: pytest $VERBOSE_FLAG $MARKER $COVERAGE_FLAG"
echo ""

# Run tests
if pytest $VERBOSE_FLAG $MARKER $COVERAGE_FLAG; then
    echo ""
    echo -e "${GREEN}✓ Tests passed!${NC}"

    # Show coverage report if generated
    if [ -n "$COVERAGE_FLAG" ]; then
        echo ""
        echo -e "${YELLOW}Coverage report generated in: htmlcov/index.html${NC}"
    fi

    exit 0
else
    echo ""
    echo -e "${RED}✗ Tests failed!${NC}"
    exit 1
fi
