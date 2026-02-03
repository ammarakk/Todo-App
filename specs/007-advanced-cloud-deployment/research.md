# Research & Technology Decisions: Phase 5

**Feature**: 007-advanced-cloud-deployment
**Date**: 2026-02-04
**Status**: Complete

## Overview

This document captures all research findings and technology decisions for Phase 5 implementation. All "NEEDS CLARIFICATION" items from the plan have been resolved through research and documented here.

---

## Decision 1: Dapr Pub/Sub with Kafka Integration

**Question**: What are the best practices for integrating Dapr Pub/Sub with Kafka?

**Decision**: Use Dapr 1.12+ with Kafka component for pub/sub abstraction.

**Research Findings**:

1. **Dapr Kafka Component Configuration**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: kafka-pubsub
   spec:
     type: pubsub.kafka
     version: v1
     metadata:
     - name: brokers
       value: "kafka:9092"
     - name: consumerGroup
       value: "todo-service"
     - name: authRequired
       value: "false"  # For local dev
   ```

2. **Publishing Events** (via Dapr HTTP API):
   ```bash
   curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
     -H "Content-Type: application/json" \
     -d '{
       "event_type": "task.created",
       "task_id": "123",
       "timestamp": "2026-02-04T10:00:00Z"
     }'
   ```

3. **Subscribing to Topics** (via Dapr subscription configuration):
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Subscription
   metadata:
     name: task-events-subscription
   spec:
     topic: task-events
     route: /events/task-events
     pubsubname: kafka-pubsub
   ```

4. **Best Practices Identified**:
   - ✅ Use consumer groups for scalable consumption (each microservice has its own group)
   - ✅ Enable auto-commit for at-least-once delivery
   - ✅ Use dead-letter topics for failed messages
   - ✅ Implement idempotent handlers (same event may be delivered multiple times)
   - ✅ Include correlation IDs in all events for distributed tracing

**Alternatives Considered**:
- **Direct Kafka client**: Rejected due to complex error handling and lack of abstraction
- **AWS SNS/SQS**: Rejected due to AWS lock-in

**References**:
- [Dapr Kafka Pub/Sub Documentation](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-kafka/)
- [Kafka Best Practices](https://www.confluent.io/blog/10-common-mistakes-in-kafka/)

---

## Decision 2: Skill Agent Design Patterns

**Question**: What are the best design patterns for reusable AI skill agents?

**Decision**: Implement skill agents as independent Python classes with dedicated prompts and structured JSON outputs.

**Research Findings**:

1. **Skill Agent Interface Pattern**:
   ```python
   # Contract for all skill agents
   from abc import ABC, abstractmethod
   from typing import Dict

   class SkillAgent(ABC):
       def __init__(self, prompt_path: str):
           self.prompt = self._load_prompt(prompt_path)

       @abstractmethod
       async def execute(self, input_text: str, context: Dict) -> Dict:
           """
           Execute skill on input text

           Returns:
               Structured JSON output matching schema
           """
           pass

       def _load_prompt(self, path: str) -> str:
           with open(path, 'r') as f:
               return f.read()
   ```

2. **Task Agent Example**:
   ```python
   class TaskAgent(SkillAgent):
       async def execute(self, input_text: str, context: Dict) -> Dict:
           prompt = f"""
           {self.prompt}

           User Input: {input_text}
           Context: {context}

           Extract task data and return JSON only.
           """

           # Call LLM (Ollama)
           response = await self._call_llm(prompt)

           # Validate JSON schema
           return self._validate_schema(response)
   ```

3. **Skill Prompt Template**:
   ```
   You are a Task Extraction Agent. Extract task data from user input.

   Return ONLY JSON in this format:
   {
     "title": "task title",
     "description": "description (optional)",
     "due_date": "ISO 8601 datetime (optional)",
     "priority": "low|medium|high",
     "tags": ["tag1", "tag2"],
     "confidence": 0.0-1.0
   }

   If missing information, set field to null and confidence < 0.7.
   ```

4. **Best Practices Identified**:
   - ✅ Separate skill prompts from system prompts (reusability)
   - ✅ Always return structured JSON (no free-form text)
   - ✅ Include confidence scores (can ask for clarification if low)
   - ✅ Use temperature=0 for deterministic outputs
   - ✅ Validate JSON schema before using output
   - ✅ Make skills stateless (all context passed as parameters)

**Alternatives Considered**:
- **Hardcoded chatbot logic**: Rejected due to unmaintainability
- **LangChain agents**: Considered but rejected for hackathon (too complex, less transparent)

**References**:
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

---

## Decision 3: Event-Driven Microservices Testing

**Question**: How to test event-driven microservices effectively?

**Decision**: Use contract testing + consumer-driven testing + integration tests with embedded Kafka.

**Research Findings**:

1. **Unit Testing (Skill Agents)**:
   ```python
   def test_task_agent_simple():
       agent = TaskAgent("prompts/task_prompt.txt")
       result = await agent.execute("Create a task to buy milk", {})

       assert result["title"] == "buy milk"
       assert result["confidence"] > 0.8
   ```

2. **Contract Testing (API Endpoints)**:
   ```python
   def test_create_task_contract():
       response = client.post("/tasks", json={
           "title": "Test Task",
           "priority": "high"
       })

       assert response.status_code == 200
       assert "task_id" in response.json()
       assert response.json()["title"] == "Test Task"
   ```

3. **Integration Testing (Kafka Events)**:
   ```python
   import pytest
   from testcontainers.kafka import KafkaContainer

   @pytest.fixture
   def kafka_container():
       kafka = KafkaContainer("confluentinc/cp-kafka:latest")
       kafka.start()
       yield kafka.get_bootstrap_server()
       kafka.stop()

   def test_task_created_event_published(kafka_container):
       # Create task via API
       response = client.post("/tasks", json={"title": "Test"})

       # Consume event from Kafka
       consumer = KafkaConsumer(
           "task-events",
           bootstrap_servers=kafka_container,
           auto_offset_reset='earliest'
       )

       event = next(consumer)
       assert event.value["event_type"] == "task.created"
   ```

4. **End-to-End Testing (Full Workflow)**:
   ```python
   def test_recurring_task_generation():
       # 1. Create recurring task
       task = client.post("/tasks", json={
           "title": "Daily standup",
           "recurrence": {"pattern": "daily"}
       })

       # 2. Complete task
       client.post(f"/tasks/{task['id']}/complete")

       # 3. Verify next task created
       tasks = client.get("/tasks").json()
       assert len([t for t in tasks if t["title"] == "Daily standup"]) == 2
   ```

5. **Best Practices Identified**:
   - ✅ Use testcontainers for embedded Kafka (no external dependencies)
   - ✅ Test idempotency (send same event twice, verify no duplicates)
   - ✅ Test failure scenarios (Kafka down, DB down)
   - ✅ Use contract tests for API stability
   - ✅ Mock LLM calls in unit tests (deterministic, fast)

**Alternatives Considered**:
- **Manual testing with external Kafka**: Rejected (slow, non-deterministic)
- **Only integration tests**: Rejected (too slow for TDD)

**References**:
- [Testcontainers for Python](https://testcontainers-python.readthedocs.io/)
- [Consumer-Driven Contract Testing](https://martinfowler.com/bliki/ConsumerDrivenContracts.html)

---

## Decision 4: Redpanda vs Kafka for Local Development

**Question**: Should we use Redpanda or Apache Kafka for local development?

**Decision**: Use Redpanda for local development (simplicity), Kafka for cloud production (standard).

**Research Findings**:

1. **Redpanda Advantages**:
   - ✅ Single binary (no ZooKeeper needed)
   - ✅ 10x faster than Kafka (C++ implementation)
   - ✅ Docker Compose friendly (single container)
   - ✅ Compatible with Kafka APIs (drop-in replacement)
   - ✅ Lower resource usage (runs on laptop)

2. **Redpanda Docker Compose**:
   ```yaml
   version: '3.8'
   services:
     redpanda:
       image: docker.redpanda.com/redpandadata/redpanda:v23.1.12
       command:
         - redpanda start
         - --overprovisioned
         - --smp 1
         - --kafka-addr 0.0.0.0:9092
       ports:
         - "9092:9092"
   ```

3. **Cloud Kafka Options**:
   - **Redpanda Cloud**: Recommended for simplicity (managed service)
   - **Confluent Cloud**: More features, higher cost
   - **Strimzi on Kubernetes**: Self-managed, more control

4. **Migration Path**:
   - Local (Redpanda) → Cloud (Redpanda Cloud): Zero code changes
   - Local (Redpanda) → Cloud (Kafka): Change broker URLs only

5. **Best Practices Identified**:
   - ✅ Use Redpanda for local dev (fast, simple)
   - ✅ Use Redpanda Cloud for production (managed, less ops)
   - ✅ Keep topic schemas identical across environments
   - ✅ Use same client library (kafka-python) everywhere

**Alternatives Considered**:
- **Apache Kafka locally**: Rejected (complex setup, requires ZooKeeper)
- **Redis Streams**: Rejected (lacks replay capability)

**References**:
- [Redpanda Documentation](https://docs.redpanda.com/)
- [Redpanda vs Kafka Comparison](https://redpanda.com/blog/redpanda-vs-kafka)

---

## Decision 5: Dapr State Management for Conversation State

**Question**: How to effectively use Dapr State Management for conversation persistence?

**Decision**: Use Dapr State Store with PostgreSQL backend for conversation state caching.

**Research Findings**:

1. **Dapr State Store Configuration**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: statestore
   spec:
     type: state.postgresql
     version: v1
     metadata:
     - name: connectionString
       value: "host=neon.db user=postgres password=*** dbname=todo"
   ```

2. **Saving Conversation State**:
   ```python
   import dapr.clients

   async def save_conversation(conversation_id: str, messages: List[Dict]):
       dapr = DaprClient()
       await dapr.save_state(
           store_name="statestore",
           key=f"conversation:{conversation_id}",
           value=json.dumps(messages)
       )
   ```

3. **Loading Conversation State**:
   ```python
   async def load_conversation(conversation_id: str) -> List[Dict]:
       dapr = DaprClient()
       state = await dapr.get_state(
           store_name="statestore",
           key=f"conversation:{conversation_id}"
       )
       return json.loads(state.data) if state.data else []
   ```

4. **State Expiration**:
   ```yaml
   metadata:
   - name: ttlInSeconds
     value: "2592000"  # 30 days
   ```

5. **Best Practices Identified**:
   - ✅ Use conversation IDs as state keys (scoped)
   - ✅ Set TTL for automatic cleanup (30 days)
   - ✅ Use JSON serialization (flexible schema)
   - ✅ Fallback to DB if state cache miss (graceful degradation)

**Alternatives Considered**:
- **Redis**: Rejected (adds another infrastructure component)
- **Pure PostgreSQL**: Rejected (slower for high-frequency reads)

**References**:
- [Dapr State Management](https://docs.dapr.io/developing-applications/building-blocks/state-management/)

---

## Decision 6: Dapr Secrets Management

**Question**: How to securely manage secrets with Dapr?

**Decision**: Use Kubernetes Secrets as the Dapr secret store (cloud-native, works locally).

**Research Findings**:

1. **Dapr Secret Store Configuration**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: kubernetes-secrets
   spec:
     type: secretstores.kubernetes
     version: v1
     metadata:
     - name: kubeconfig
       value: "/path/to/kubeconfig"  # Optional for local dev
   ```

2. **Creating Kubernetes Secrets**:
   ```bash
   kubectl create secret generic db-credentials \
     --from-literal=username=postgres \
     --from-literal=password=secretpass \
     --from-literal=host=neon.db
   ```

3. **Fetching Secrets in Code**:
   ```python
   import dapr.clients

   async def get_db_credentials() -> Dict:
       dapr = DaprClient()
       secret = await dapr.get_secret(
           store_name="kubernetes-secrets",
           key="db-credentials"
       )
       return secret.secret
   ```

4. **Best Practices Identified**:
   - ✅ Never log secrets (use structured logging with redaction)
   - ✅ Use separate secrets per environment (dev/staging/prod)
   - ✅ Rotate secrets regularly (Kubernetes secret rotation)
   - ✅ Never commit secrets to git (use .gitignore)

**Alternatives Considered**:
- **HashiCorp Vault**: Rejected (overkill for hackathon)
- **AWS Secrets Manager**: Rejected (AWS lock-in)

**References**:
- [Dapr Secrets Management](https://docs.dapr.io/developing-applications/building-blocks/secrets/)

---

## Decision 7: Real-Time Updates Strategy

**Question**: How to implement real-time updates across clients?

**Decision**: Use Dapr Pub/Sub with WebSocket subscriptions in frontend.

**Research Findings**:

1. **Backend Publishes Updates**:
   ```python
   async def publish_task_update(task_id: str, update_data: Dict):
       await dapr.publish_event(
           pubsub_name="kafka-pubsub",
           topic_name="task-updates",
           data={
               "event_type": "task.updated",
               "task_id": task_id,
               "data": update_data,
               "timestamp": datetime.utcnow().isoformat()
           }
       )
   ```

2. **Frontend Subscribes via WebSocket**:
   ```javascript
   const ws = new WebSocket('ws://backend:3500/v1.0/subscribe/task-updates');

   ws.onmessage = (event) => {
     const update = JSON.parse(event.data);
     if (update.event_type === 'task.updated') {
       updateTaskInUI(update.task_id, update.data);
     }
   };
   ```

3. **Dapr Subscription Configuration**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Subscription
   metadata:
     name: task-updates-subscription
   spec:
     topic: task-updates
     route: /events/task-updates
     pubsubname: kafka-pubsub
   ```

4. **Backend WebSocket Endpoint**:
   ```python
   from fastapi import WebSocket

   @app.websocket("/events/task-updates")
   async def task_updates_websocket(websocket: WebSocket):
       await websocket.accept()
       # Dapr pushes events to this endpoint
       # Forward to connected clients
   ```

5. **Best Practices Identified**:
   - ✅ Use connection IDs for client tracking
   - ✅ Implement heartbeat/ping (detect stale connections)
   - ✅ Batch rapid updates (prevent client overload)
   - ✅ Handle reconnections gracefully (auto-reconnect on disconnect)

**Alternatives Considered**:
- **Server-Sent Events (SSE)**: Considered (simpler, but unidirectional)
- **Polling**: Rejected (inefficient, high latency)

**References**:
- [Dapr Pub/Sub](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)

---

## Summary of Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Event Bus** | Kafka (Redpanda local, Kafka cloud) | Industry standard, replay capability, scalable |
| **Pub/Sub Abstraction** | Dapr 1.12+ | Vendor-neutral, best practices built-in |
| **State Store** | Dapr + PostgreSQL | Cloud-portable, familiar SQL |
| **Secrets** | Kubernetes Secrets via Dapr | Cloud-native, works locally |
| **Skill Agents** | Python classes with prompts | Reusable, testable, hackathon-friendly |
| **Real-Time Updates** | Dapr Pub/Sub + WebSocket | Scalable, decoupled, bidirectional |
| **Testing** | pytest + testcontainers | Fast, deterministic, no external deps |

---

## Next Steps

With all research complete and decisions documented:

1. ✅ **Phase 0 Complete**: All "NEEDS CLARIFICATION" items resolved
2. → **Phase 1**: Generate `data-model.md` with entity schemas
3. → **Phase 1**: Generate API and event contracts in `contracts/`
4. → **Phase 1**: Generate `quickstart.md` for developer setup
5. → **Phase 2**: Run `/sp.tasks` to break down into actionable implementation tasks

---

**Research Status**: ✅ Complete - All technology decisions finalized and documented
