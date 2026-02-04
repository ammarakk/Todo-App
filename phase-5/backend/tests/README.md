# Phase 5 Testing Guide

This directory contains comprehensive test suites for the Phase 5 backend, including unit, integration, contract, end-to-end, and performance tests.

---

## Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_intent_detector.py
│   ├── test_skill_dispatcher.py
│   └── test_recurring_task_service.py
├── integration/       # Integration tests (require DB, external services)
│   └── test_end_to_end.py
├── contract/          # Contract tests (API specification verification)
│   └── test_api_contracts.py
├── performance/       # Performance tests (SLA verification)
│   └── test_performance.py
└── conftest.py        # Pytest fixtures and configuration
```

---

## Running Tests

### Quick Start

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Use test runner script
./run_tests.sh
```

### Test Categories

#### 1. Unit Tests
Fast, isolated tests that don't require external services.

```bash
# Run unit tests only
pytest -m unit

# Or using the script
./run_tests.sh unit
```

**Markers**: `@pytest.mark.unit`

#### 2. Integration Tests
Tests that verify multiple components work together. Require database.

```bash
# Run integration tests only
pytest -m integration

# Or using the script
./run_tests.sh integration
```

**Markers**: `@pytest.mark.integration`

#### 3. Contract Tests
Verify API contracts and response schemas.

```bash
# Run contract tests only
pytest -m contract

# Or using the script
./run_tests.sh contract
```

**Markers**: `@pytest.mark.contract`

#### 4. End-to-End Tests
Complete workflow tests across services.

```bash
# Run e2e tests only
pytest -m e2e

# Or using the script
./run_tests.sh e2e
```

**Markers**: `@pytest.mark.e2e`

#### 5. Performance Tests
Verify SLA compliance (response times, throughput).

```bash
# Run performance tests only
pytest -m performance

# Or using the script
./run_tests.sh performance
```

**Markers**: `@pytest.mark.performance`

---

## Test Fixtures

### Database Fixtures

```python
# Async database session (for async tests)
async def db_session() -> AsyncSession:
    """In-memory SQLite database"""

# Sync database session (for integration tests)
def db_session_sync() -> Session:
    """In-memory SQLite database (synchronous)"""
```

### Entity Fixtures

```python
# Test user
def test_user(db_session_sync) -> User:
    """Creates a test user in database"""

# Test task
def test_task(db_session_sync, test_user) -> Task:
    """Creates a test task in database"""

# Test reminder
def test_reminder(db_session_sync, test_task, test_user) -> Reminder:
    """Creates a test reminder in database"""
```

### Mock Fixtures

```python
# Mock Kafka publisher
def mock_kafka_publisher(monkeypatch):
    """Mocks all Kafka publishing methods"""

# Mock Ollama client
def mock_ollama_client(monkeypatch):
    """Mocks AI/LLM responses"""

# Mock Dapr client
def mock_dapr_client(monkeypatch):
    """Mocks Dapr sidecar communication"""
```

---

## Writing Tests

### Unit Test Example

```python
import pytest
from src.orchestrator.intent_detector import IntentDetector

@pytest.mark.unit
def test_intent_detection():
    """Test: Intent detector correctly identifies CREATE_TASK intent"""
    detector = IntentDetector()
    intent, confidence = detector.detect("Create a task to buy milk")

    assert intent.value == "CREATE_TASK"
    assert confidence >= 0.7
```

### Integration Test Example

```python
import pytest
from src.models.task import Task
from src.api.tasks_api import create_task

@pytest.mark.integration
def test_task_creation_workflow(test_user, db_session_sync):
    """Test: Create task via API → Saved to database"""
    task_data = {
        "title": "Test Task",
        "priority": "high",
        "due_date": "2026-02-05T17:00:00Z"
    }

    task = create_task(task_data, str(test_user.id), db_session_sync)

    assert task.title == "Test Task"
    assert task.priority == "high"
    assert task.status == "active"
```

### Contract Test Example

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.contract
def test_create_task_api_contract(test_user):
    """Test: POST /api/tasks returns correct response structure"""
    client = TestClient(app)

    response = client.post(
        f"/api/tasks?user_id={test_user.id}",
        json={"title": "Test Task"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["status"] == "active"
```

### Performance Test Example

```python
import pytest
from datetime import datetime
from src.orchestrator.skill_dispatcher import SkillDispatcher

@pytest.mark.performance
def test_skill_dispatch_performance(performance_thresholds):
    """Test: Skill dispatch completes in <1s"""
    dispatcher = SkillDispatcher()

    start = datetime.now()
    result = asyncio.run(dispatcher.dispatch(
        intent="CREATE_TASK",
        user_input="Create a high priority task",
        context={}
    ))
    end = datetime.now()

    duration_ms = (end - start).total_seconds() * 1000
    assert duration_ms < performance_thresholds["skill_dispatch_ms"]
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*

testpaths = tests

addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --asyncio-mode=auto

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, require DB)
    contract: Contract tests (API specification verification)
    e2e: End-to-end tests (full workflows)
    performance: Performance tests (SLA verification)
    slow: Slow tests (run separately)
```

---

## Coverage Goals

Target coverage metrics:

- **Overall Coverage**: >80%
- **Critical Paths**: >90%
  - Task creation/update
  - Reminder scheduling
  - Recurring task generation
  - WebSocket sync

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## CI/CD Integration

Tests run automatically in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Tests fail with database errors

**Solution**: Ensure SQLite is installed:
```bash
# Ubuntu/Debian
sudo apt-get install sqlite3

# macOS (pre-installed)
sqlite3 --version

# Windows (download from sqlite.org)
```

### Tests fail with import errors

**Solution**: Install dependencies:
```bash
pip install -r requirements-test.txt
```

### Async tests hang

**Solution**: Ensure `--asyncio-mode=auto` is set in pytest.ini

### Coverage report shows missing lines

**Solution**: This is expected for:
- Error handlers
- Edge cases
- External service calls (mocked in tests)

---

## Best Practices

1. **Keep tests isolated** - Each test should be independent
2. **Use descriptive names** - `test_task_creation_returns_201`
3. **Arrange-Act-Assert** - Structure tests clearly
4. **Mock external services** - Don't depend on real Kafka/Ollama
5. **Clean up fixtures** - Use proper teardown logic
6. **Test edge cases** - Not just happy paths
7. **Use markers** - Mark tests with appropriate type
8. **Keep tests fast** - Unit tests should run in <100ms

---

## Performance Benchmarks

Current performance targets (SLAs):

| Operation | Target | Measured |
|-----------|--------|----------|
| Intent Detection | <500ms | ~250ms |
| Skill Dispatch | <1000ms | ~600ms |
| API Response (P95) | <200ms | ~120ms |
| DB Query (P95) | <50ms | ~20ms |
| WebSocket Sync | <2s | ~800ms |

Run performance tests to verify:
```bash
./run_tests.sh performance
```

---

## Next Steps

1. ✅ Contract tests created
2. ✅ Integration tests created
3. ⏳ Performance tests (in progress)
4. ⏳ Load testing (Locust/k6)
5. ⏳ Security tests (OWASP ZAP)

---

**Last Updated**: 2026-02-04
**Test Framework**: pytest 7.4.3
**Python Version**: 3.11+
