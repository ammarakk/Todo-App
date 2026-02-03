<!--
Sync Impact Report:
===================
Version: 4.0.0 → 5.0.0 (MAJOR - Phase V: Production-Ready Event-Driven Microservices with AI Skills)
Modified Principles:
  - Phase III (AI-Native) - LOCKED, preserved unchanged
  - Phase IV (Infrastructure & DevOps) - LOCKED, preserved unchanged
  - Phase V (Production-Ready Advanced AI) - NEW principles added
Added Sections:
  - Phase V Core Principles (7 new principles for production AI)
  - Skills & Agents Architecture (reusable AI modules)
  - Event-Driven Microservices (Kafka + Dapr)
  - Backend Brain Controller (AI orchestrator)
  - System Prompts Layer (global behavior control)
  - Repository & Folder Strategy (phase-5 structure)
  - CI/CD & Reliability Requirements
  - Testing & Security Standards
  - Judge-Friendly Architecture (hackathon reusability)
Removed Sections: None
Templates Requiring Updates:
  - ✅ .specify/templates/plan-template.md (validated - generic structure supports Phase V microservices)
  - ✅ .specify/templates/spec-template.md (validated - supports event-driven specs)
  - ✅ .specify/templates/tasks-template.md (validated - supports skill agent task categorization)
  - ✅ .specify/templates/commands/*.md (validated for Phase V compatibility)
  - ✅ .specify/templates/phr-template.prompt.md (validated - supports constitution stage)
Follow-up TODOs: None - all placeholders filled, Phase V ready for implementation
-->

# Evolution of Todo Constitution - Phase V (Production-Ready Event-Driven AI System)

## Phase Context

This constitution governs the evolution of the "Evolution of Todo" project through **spec-driven development**, powered by Claude Code and SpecKit Plus.

### Phase Status
- **Phase III**: LOCKED - AI-Native Todo System with Qwen + MCP (stable, production-ready)
- **Phase IV**: LOCKED - Infrastructure, Containerization, Kubernetes, and DevOps automation
- **Phase V**: ACTIVE - Event-driven microservices, AI skills agents, production-ready architecture
- **Phase VI+**: FUTURE - Advanced AI multi-agent systems and cloud deployment

### Core Objective (Phase V)

Transform the Phase IV application into a **production-ready, event-driven AI system** with:
- Reusable AI skill agents (not hardcoded chatbot logic)
- Event-driven microservices architecture (Kafka + Dapr)
- Backend as AI orchestrator (brain controller)
- System prompts layer (global behavior control)
- CI/CD automation and production reliability
- **Judge-friendly reusability framework** for future hackathons

**CRITICAL**: Phase V is Phase IV **FIXED + STABILIZED + DISTRIBUTED + CLOUD-READY**. NOT a rewrite. NOT experimental.

---

## Phase III Principles (LOCKED - Must Not Modify)

### I. AI-Native Interaction

The chatbot MUST be the primary interface for task management, not an add-on. All CRUD operations MUST be accessible through natural language commands in English and Urdu. The AI agent MUST maintain context across conversations to provide coherent, personalized assistance.

**Rationale**: Users expect conversational interfaces that understand context and intent, not rigid command-line interfaces. AI-native design ensures natural task management.

### II. Stateless Server Architecture

The backend MUST hold NO session state. Every request MUST be independent, fetching conversation history from the database to build the message array for the agent. All state MUST be persisted in Neon PostgreSQL.

**Rationale**: Stateless design enables horizontal scaling, fault tolerance, and clean separation of concerns. Server restarts MUST NOT lose conversation context.

### III. Persistence of Intelligence

All chat sessions MUST be stored in `Conversation` and `Message` tables to ensure context is maintained across server restarts. Every user interaction MUST be traceable and replayable for debugging and improvement.

**Rationale**: Context persistence is essential for usable AI assistants. Users MUST NOT lose conversation history due to server issues.

### IV. Strict Security & User Isolation

Every chat request MUST verify the Better Auth JWT token from Phase II. The AI agent is STRICTLY PROHIBITED from accessing or modifying any task that does not belong to the authenticated `user_id`. All database queries MUST include user_id filters.

**Rationale**: Multi-tenant systems require absolute isolation. Security vulnerabilities are unacceptable in user data systems.

### V. Multi-Language Support

The chatbot MUST support Urdu and English for both input commands and assistant responses. The AI MUST automatically detect language and respond in kind. Action confirmations MUST be provided in the user's language.

**Rationale**: Accessibility and inclusivity are non-negotiable. Language barriers MUST NOT prevent task management.

### VI. MCP-First Tool Design

All task operations MUST be exposed as Model Context Protocol (MCP) tools using the Official MCP SDK. The AI agent MUST interact with the system ONLY through these tools, never through direct database access.

**Rationale**: MCP provides a standardized, secure, and observable interface for AI agents. Direct database access bypasses critical security and validation layers.

---

## Phase IV Principles (LOCKED - Must Not Modify)

### VII. Immutable Phase III Business Logic

Phase IV **MUST NOT modify** any application logic from Phase III. All changes MUST be infrastructure-level: Dockerfiles, Kubernetes manifests, Helm charts, and CI/CD pipelines. The /apps/todo-frontend and /apps/todo-backend code MUST remain functionally identical to Phase III.

**Rationale**: Business logic stability is critical. Phase IV focuses purely on deployment, scaling, and operational concerns. This ensures Phase III features remain fully functional while infrastructure evolves.

### VIII. Spec-Driven Infrastructure

All Docker, Kubernetes, and Helm configurations MUST be generated by Claude Code through the spec-driven workflow: `/sp.constitution → /sp.specify → /sp.plan → /sp.tasks → /sp.implement`. NO manual YAML/Dockerfile authoring is permitted. AI tools (kubectl-ai, kagent, Gordon) MUST be used for all infrastructure generation.

**Rationale**: Infrastructure-as-code generated by AI tools is more consistent, follows best practices, and reduces human error. Manual coding leads to configuration drift and security vulnerabilities.

### IX. Ollama-First LLM Runtime

Phase IV **MUST use Ollama** as the LLM runtime container. All chatbot services MUST connect to Ollama via its HTTP API. The chatbot service acts as an adapter, converting user messages to Ollama prompts and parsing responses into structured API calls to the backend.

**Rationale**: Ollama provides local, privacy-preserving inference with no external API dependencies. It simplifies deployment and reduces latency compared to cloud-based inference services.

### X. Kubernetes-Native Deployment

All services MUST be deployed on Kubernetes (Minikube for local) using Helm charts. Service discovery, load balancing, and configuration MUST be handled by Kubernetes primitives (Services, ConfigMaps, Secrets). Manual port mapping and container linking are PROHIBITED.

**Rationale**: Kubernetes provides production-grade orchestration: auto-scaling, self-healing, and rolling updates. Helm charts enable versioned, reproducible deployments across environments.

### XI. AI-Powered DevOps Automation

Phase IV MUST leverage AI DevOps tools for all operational tasks:
- **kubectl-ai**: Deploy, scale, debug services via natural language
- **kagent**: Monitor cluster health, optimize resource usage, detect anomalies
- **Gordon/Docker AI**: Generate optimal container images, multi-stage builds, security scanning

**Rationale**: AI-powered DevOps reduces operational overhead, improves reliability, and enables self-healing infrastructure. Human operators focus on architecture, not repetitive tasks.

---

## Phase V Core Principles (NEW)

### XII. Skills & Agents Architecture (MANDATORY)

All AI capabilities MUST be implemented as **reusable skill agents**, not hardcoded chatbot logic. Each skill is an independent, testable module with:

1. **Dedicated prompt** in `/system_prompts/` or `/agents/skills/prompts/`
2. **Structured JSON output** (no free-form text)
3. **Clear responsibility** (single purpose per skill)
4. **Reusability** (can be used in any future AI project)

**Required Skills**:
- **Task Agent**: Extract task data from natural language (title, priority, description)
- **Reminder Agent**: Extract time, date, timezone from user messages
- **Recurring Agent**: Calculate next occurrence for recurring tasks (daily, weekly, monthly)
- **Audit Agent**: Log all system actions for compliance and debugging

**Rationale**: Hardcoded AI logic is unmaintainable and unreproducible. Skill agents provide:
- **Testability**: Each skill can be unit tested independently
- **Reusability**: Skills can be copied to future hackathon projects
- **Judge Appeal**: Demonstrates professional AI architecture
- **Maintainability**: Changes to one skill don't break others

### XIII. System Prompts Layer (Global Behavior Control)

System prompts define **global AI behavior** separate from task-specific skills. System prompts control:

1. **Task assistant rules**: How the AI should behave overall
2. **Clarification logic**: When to ask user for missing information
3. **Error handling language**: How to present failures to users
4. **Output discipline**: Format requirements for all responses
5. **Conversation flow**: How to maintain context across turns

**System prompts location**: `/system_prompts/` at project root
**Skill prompts location**: `/agents/skills/prompts/`

**Rationale**: Separating system behavior from task skills enables:
- **Global behavior changes** without touching individual skills
- **Consistent user experience** across all AI interactions
- **Easy A/B testing** of prompt strategies
- **Professional AI engineering** (industry standard pattern)

### XIV. Backend as AI Orchestrator (Brain Controller)

The backend API MUST act as **AI orchestrator**, not a simple CRUD server. Orchestrator flow:

1. **Receive message** from user (via frontend or chatbot)
2. **Load system prompt** from `/system_prompts/`
3. **Detect intent** (create task, set reminder, list todos, etc.)
4. **Call appropriate skill agent** based on intent
5. **Validate skill output** (structured JSON validation)
6. **Execute business logic** (database operations via MCP tools)
7. **Publish Kafka event** for microservices (notifications, recurring, audit)
8. **Return response** to user in their language

**Rationale**: Central orchestration prevents "chatbot confusion" where different parts of the system conflict. This is how production AI systems are built (e.g., Alexa, Siri, ChatGPT plugins).

### XV. Event-Driven Microservices (Decoupled Architecture)

All cross-cutting concerns MUST be implemented as **event-driven microservices**, not direct function calls:

**Microservices**:
- **Notification Service**: Listens to `reminder.events`, triggers notifications
- **Recurring Service**: Listens to `task.completed` events, generates next recurring task
- **Audit Service**: Listens to all events, logs to audit database

**Event Bus**: Kafka (dev: Redpanda for simplicity)
**Pub/Sub Layer**: Dapr (abstracts Kafka, provides retries, dead-letter queues)

**Rationale**:
- **Decoupling**: Services can scale independently
- **Reliability**: Events persist even if services are down
- **Judge Appeal**: Microservices = professional architecture
- **Future-Proof**: Easy to add new services without breaking existing ones

### XVI. Dapr Integration (Cloud Portability)

Dapr MUST be used for all cross-service communication:
- **Pub/Sub**: Publish/subscribe events via Kafka
- **State Management**: Store conversation context, user preferences
- **Secrets Management**: Fetch secrets from Kubernetes Secrets
- **Service Invocation**: Call other services with automatic retries

**Rationale**: Dapr provides **vendor-neutral** abstractions:
- Easy migration from local (Docker Compose) to cloud (Kubernetes)
- No hardcoded Kafka or Redis dependencies
- Industry-standard for cloud-native applications
- Judges love "production-grade" infrastructure

### XVII. CI/CD Automation (Production Deployment)

All deployments MUST be automated via CI/CD pipeline:

**Pipeline Stages**:
1. **Code**: Push to git (protected main branch)
2. **Test**: Run unit tests, integration tests, contract tests
3. **Build**: Create Docker images with semantic versioning
4. **Security Scan**: Check for CVEs in dependencies
5. **Push**: Upload images to container registry (Docker Hub, GHCR)
6. **Deploy**: Helm upgrade to Kubernetes (zero-downtime)
7. **Verify**: Run smoke tests against deployed services

**Tools**: GitHub Actions or GitLab CI (choose one)
**Requirement**: Manual approval required for production deployment

**Rationale**: Manual deployment is error-prone and unprofessional. CI/CD ensures:
- **Consistency**: Same process for dev, staging, production
- **Speed**: Deployments in minutes, not hours
- **Reliability**: Tests catch bugs before production
- **Judge Appeal**: Demonstrates DevOps maturity

### XVIII. Production Reliability (Non-Negotiable Standards)

All services MUST meet **production reliability standards**:

**Health & Readiness**:
- ✅ `/health` endpoint (liveness probe - is service running?)
- ✅ `/ready` endpoint (readiness probe - is service ready for traffic?)
- ✅ Resource limits defined (CPU, memory) in Kubernetes
- ✅ Restart policy (always restart on failure)

**Error Handling**:
- ✅ Retry logic with exponential backoff (for external calls)
- ✅ Circuit breaker (stop calling failing services)
- ✅ Timeout handling (no hanging requests)
- ✅ Graceful degradation (fallback to basic features if AI fails)

**Logging & Observability**:
- ✅ Structured JSON logs (not print statements)
- ✅ Correlation IDs (trace requests across services)
- ✅ Log aggregation (ELK stack or Loki)
- ✅ Metrics (Prometheus) for critical operations

**Rationale**: Production systems fail unpredictably. These standards ensure:
- **Self-healing**: Kubernetes automatically restarts failed services
- **Debuggability**: Logs enable quick troubleshooting
- **Reliability**: System degrades gracefully, not catastrophically
- **Judge Appeal**: Professional-grade operations

---

## Repository & Folder Strategy (Phase V)

### Structure

```
/phase-5
  /frontend              # Phase IV copy (READ-ONLY - no modifications)
  /backend               # Phase IV copy + AI orchestrator logic
  /agents
    /skills              # Reusable AI skill modules
      /task_agent.py     # Extract task data from text
      /reminder_agent.py # Extract time/date from text
      /recurring_agent.py# Calculate next recurring date
      /audit_agent.py    # Log system actions
    /prompts             # Skill-specific prompts
      /task_prompt.txt
      /reminder_prompt.txt
      /recurring_prompt.txt
  /system_prompts        # Global behavior control
    /global_behavior.txt      # Overall AI personality
    /clarification_logic.txt  # How to ask for missing info
    /error_handling.txt       # How to present errors
  /microservices        # Event-driven services
    /notification       # Reminder notification service
    /recurring          # Auto-generate recurring tasks
    /audit              # Audit logging service
  /kafka                # Kafka configuration (dev: Redpanda)
  /dapr                 # Dapr components and configuration
  /helm                 # Helm charts (enhanced from Phase IV)
  /tests                # Comprehensive test suite
    /unit               # Skill agent unit tests
    /integration        # End-to-end workflow tests
    /contract           # API contract tests
  /docs                 # Phase V documentation
```

### Key Constraints

- **/frontend**: Phase IV copy - NO modifications permitted
- **/backend**: Phase IV copy + orchestrator logic only (no CRUD changes)
- **/agents/skills**: MUST be reusable (no hardcoded business logic)
- **/microservices**: Event-driven only - NO direct function calls to backend
- **/system_prompts**: Global behavior - applies to all AI interactions

**Rationale**: Clear separation enables:
- **Independent testing** of each component
- **Easy reuse** of skill agents in future projects
- **Scalability** of microservices
- **Judge-friendly** architecture demonstration

---

## Skills & Agents Architecture

### Skill Agent Contract

Every skill agent MUST follow this contract:

```python
# Skill Agent Interface (pseudocode)
class SkillAgent:
    def __init__(self, prompt_path: str):
        """Load skill-specific prompt from /agents/skills/prompts/"""
        self.prompt = load_prompt(prompt_path)

    async def execute(self, input_text: str, context: dict) -> dict:
        """
        Execute skill on input text

        Args:
            input_text: User's natural language input
            context: Additional context (user_id, conversation_history, etc.)

        Returns:
            Structured JSON output (MUST match schema)

        Raises:
            SkillExecutionError: If skill fails
            ValidationError: If output doesn't match schema
        """
        # 1. Build prompt from template + input
        # 2. Call LLM (Ollama/Qwen API)
        # 3. Parse response to JSON
        # 4. Validate against schema
        # 5. Return structured output
```

### Required Skills

#### Task Agent
- **Prompt**: `/agents/skills/prompts/task_prompt.txt`
- **Input**: User message (e.g., "create a task to buy groceries")
- **Output**:
  ```json
  {
    "title": "buy groceries",
    "priority": "MEDIUM",
    "description": null,
    "due_date": null
  }
  ```
- **Error**: Returns `null` if no task detected

#### Reminder Agent
- **Prompt**: `/agents/skills/prompts/reminder_prompt.txt`
- **Input**: User message (e.g., "remind me tomorrow at 3pm")
- **Output**:
  ```json
  {
    "reminder_time": "2026-02-05T15:00:00",
    "timezone": "UTC",
    "message": "remind me tomorrow at 3pm"
  }
  ```
- **Error**: Returns `null` if no time detected

#### Recurring Agent
- **Prompt**: `/agents/skills/prompts/recurring_prompt.txt`
- **Input**: Task + recurring rule (e.g., "daily standup", "every Monday")
- **Output**:
  ```json
  {
    "next_date": "2026-02-06T10:00:00",
    "frequency": "WEEKLY",
    "interval": 1
  }
  ```

#### Audit Agent
- **Prompt**: None (rule-based, no LLM needed)
- **Input**: Any system event
- **Output**: Log entry to audit database

### Skill Reusability

Skills MUST be designed for reuse:
- **No hardcoded business logic** (e.g., no database tables in skills)
- **Generic prompts** (work for any domain, not just todos)
- **Schema validation** (clear input/output contracts)
- **Unit tests** (testable without full system)

**Reuse Example**: Task Agent can be used in future projects:
- Project A: Todo app (extract tasks from chat)
- Project B: Email client (extract tasks from emails)
- Project C: Meeting app (extract action items from transcripts)

**Rationale**: This reusability is a **competitive advantage** for hackathons. Judges see:
- Professional AI engineering
- Thoughtful architecture
- Future-ready codebase
- Time-saving framework for next project

---

## Event-Driven Microservices

### Architecture

```
Backend API (Orchestrator)
    │
    ├─> Publishes Kafka Events
    │   ├─> task.created
    │   ├─> task.completed
    │   ├─> reminder.scheduled
    │   └─> user.action
    │
    └─> Dapr Pub/Sub
        │
        ├─> Notification Service (subscribes to reminder.scheduled)
        ├─> Recurring Service (subscribes to task.completed)
        └─> Audit Service (subscribes to all events)
```

### Microservice Contracts

#### Notification Service
- **Trigger**: `reminder.scheduled` event
- **Action**: Send notification (email, push, in-app)
- **Tech**: FastAPI + Dapr SDK
- **Scaling**: Independent (can scale to 10+ replicas)

#### Recurring Service
- **Trigger**: `task.completed` event where `is_recurring=true`
- **Action**: Create next task in sequence
- **Logic**: Calculate next date based on frequency
- **Tech**: FastAPI + Dapr SDK

#### Audit Service
- **Trigger**: All events
- **Action**: Log to audit database
- **Purpose**: Compliance, debugging, analytics
- **Tech**: FastAPI + PostgreSQL (separate from main DB)

### Dapr Integration

**Dapr Components**:
- **Pub/Sub**: Kafka (dev: Redpanda)
- **State Store**: Redis (for caching, session data)
- **Secrets**: Kubernetes Secrets

**Example Usage** (pseudocode):
```python
# Backend publishes event
from dapr.clients import DaprClient

with DaprClient() as dapr:
    dapr.publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="task.created",
        data=json.dumps({"task_id": 123, "user_id": 456})
    )

# Notification service subscribes
@app.post("/subscribe/reminder-scheduled")
async def handle_reminder(event: dict):
    # Send notification
    send_notification(event["user_id"], event["message"])
```

**Rationale**: Dapr provides **production-grade** abstractions:
- No hardcoded Kafka client code
- Automatic retries and dead-letter queues
- Easy switching between dev (Redpanda) and prod (Kafka)
- Judges love "cloud-native" buzzwords

---

## Backend Brain Controller

### Orchestrator Flow

```python
# Backend API - AI Orchestrator (pseudocode)
async def process_message(user_message: str, user_id: int):
    # 1. Load system prompt
    system_prompt = load_system_prompt("/system_prompts/global_behavior.txt")

    # 2. Build conversation context
    conversation = get_conversation_history(user_id)

    # 3. Detect intent (using LLM or rule-based)
    intent = detect_intent(user_message, conversation)

    # 4. Route to appropriate skill agent
    if intent == "CREATE_TASK":
        skill_agent = TaskAgent()
        skill_output = await skill_agent.execute(user_message, {"user_id": user_id})

        # 5. Execute business logic via MCP tools
        result = mcp_create_task(
            title=skill_output["title"],
            priority=skill_output["priority"],
            user_id=user_id
        )

        # 6. Publish Kafka event
        publish_event("task.created", {"task_id": result["id"], "user_id": user_id})

        # 7. Return response
        return {"message": "Task created successfully", "task": result}

    elif intent == "SET_REMINDER":
        skill_agent = ReminderAgent()
        skill_output = await skill_agent.execute(user_message, {"user_id": user_id})

        # Create reminder in database
        result = create_reminder(
            user_id=user_id,
            time=skill_output["reminder_time"],
            message=skill_output["message"]
        )

        # Publish event for notification service
        publish_event("reminder.scheduled", {"reminder_id": result["id"]})

        return {"message": "Reminder set successfully"}

    # ... handle other intents
```

### Intent Detection

**Approach 1**: LLM-based (Ollama/Qwen API)
- Prompt: "Classify this message: CREATE_TASK, SET_REMINDER, LIST_TODOS, etc."
- Flexible, handles new patterns

**Approach 2**: Rule-based (regex/keyword matching)
- Fast, 100% reliable
- Use as fallback if LLM fails

**Hybrid**: Try LLM first, fallback to rules (matches Phase IV chatbot design)

---

## System Prompts Layer

### Global Behavior Prompt

**Location**: `/system_prompts/global_behavior.txt`

**Content** (example):
```
You are a helpful task assistant. Your role is to help users manage their tasks efficiently.

Guidelines:
- Be concise and friendly
- Ask for clarification when information is missing
- Confirm actions before executing them (if high-risk)
- Use the same language as the user (English or Urdu)
- Present errors in a user-friendly way

Output format:
- Always return structured JSON
- Include confidence scores for uncertain information
- Flag when user input is ambiguous
```

### Clarification Logic Prompt

**Location**: `/system_prompts/clarification_logic.txt`

**Content** (example):
```
When to ask for clarification:
1. Task title is missing or unclear
2. Priority is implied but not stated (ask if time-sensitive)
3. Due date is mentioned but time/timezone is ambiguous
4. User mentions multiple tasks in one message

How to ask:
- Be specific about what information is needed
- Provide examples if helpful
- Don't ask for optional information
```

### Error Handling Prompt

**Location**: `/system_prompts/error_handling.txt`

**Content** (example):
```
Error response guidelines:
1. Acknowledge the error clearly
2. Explain what went wrong (in simple terms)
3. Suggest how to fix it
4. Never expose internal system details
5. Apologize if the error is system's fault

Example responses:
- "I couldn't create the task because the title is missing. Could you please provide a task title?"
- "Sorry, I'm having trouble connecting to the database. Please try again in a moment."
```

---

## CI/CD Pipeline

### Pipeline Definition

**Tool**: GitHub Actions (or GitLab CI)

**Stages**:

```yaml
# .github/workflows/deploy.yml (simplified)
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit/          # Unit tests
      - run: pytest tests/integration/   # Integration tests
      - run: pytest tests/contract/      # Contract tests

  build:
    needs: test
    steps:
      - run: docker build -t todo-app/backend:${{ github.sha }} .
      - run: docker push todo-app/backend:${{ github.sha }}
      - run: trivy image todo-app/backend:${{ github.sha }}  # Security scan

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - run: helm upgrade todo-app ./helm --install --namespace staging

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production  # Requires manual approval
    steps:
      - run: helm upgrade todo-app ./helm --install --namespace production
      - run: ./scripts/smoke-tests.sh  # Verify deployment
```

### Required Tests

**Unit Tests**:
- Each skill agent (test with sample inputs)
- Business logic (CRUD operations)
- Intent detection (rule-based and LLM-based)

**Integration Tests**:
- End-to-end workflows (create task via chat → verify in database)
- Kafka event publishing (verify events are published)
- Dapr pub/sub (verify microservices receive events)

**Contract Tests**:
- API endpoints match OpenAPI spec
- Skill agent outputs match schemas
- Event payloads match expected format

**Smoke Tests** (post-deployment):
- Frontend loads
- Backend /health returns 200
- Chatbot responds to "hello"
- All pods are running

---

## Testing Requirements

### Test Coverage Goals

- **Unit tests**: 80%+ coverage for skill agents and business logic
- **Integration tests**: All user journeys covered
- **Contract tests**: All API endpoints covered
- **E2E tests**: Critical paths (login, create task, set reminder)

### Test Data Management

- **Unit tests**: Use fixtures (no external dependencies)
- **Integration tests**: Use test database (PostgreSQL test instance)
- **E2E tests**: Use separate test environment (not production)

### Test Automation

- **Pre-commit**: Run unit tests and linting
- **Pre-push**: Run integration tests
- **Pre-deploy**: Run full test suite + smoke tests
- **Post-deploy**: Run smoke tests against production

---

## Security Standards

### Secrets Management

- ✅ **No hardcoded secrets** in code or configs
- ✅ **Dapr secrets store** for runtime secret access
- ✅ **Kubernetes Secrets** for deployment-time secrets
- ✅ **Environment-specific** secrets (dev, staging, prod)
- ✅ **Secret rotation** policy (every 90 days)

### Input Validation

- ✅ **Sanitize all user input** (SQL injection, XSS prevention)
- ✅ **Validate skill agent outputs** (schema validation)
- ✅ **Rate limiting** on API endpoints (prevent abuse)
- ✅ **JWT authentication** on all protected endpoints

### Network Security

- ✅ **Service mesh** (optional) for mTLS
- ✅ **Network policies** in Kubernetes (restrict pod communication)
- ✅ **Ingress TLS** for external access
- ✅ **Private Kafka cluster** (not exposed to internet)

---

## Performance Requirements

### Response Time Goals

- **Skill agent execution**: < 2 seconds (p95)
- **Backend API response**: < 1 second (p95)
- **Chatbot end-to-end**: < 5 seconds (p95)
- **Kafka event delivery**: < 100ms (p95)

### Scalability Goals

- **Frontend**: 10+ replicas (horizontal scaling)
- **Backend**: 5+ replicas (horizontal scaling)
- **Microservices**: Independent scaling (notification: 10+, recurring: 2+)
- **Kafka**: Partitioned topics for parallelism

### Resource Efficiency

- **Frontend pod**: 128Mi CPU, 256Mi memory
- **Backend pod**: 256Mi CPU, 512Mi memory
- **Microservice pod**: 128Mi CPU, 256Mi memory
- **Total cluster**: < 8 CPU cores, < 16Gi memory (dev environment)

---

## Judge-Friendly Architecture

### What Judges See

Judges evaluate hackathon projects on:

1. **Innovation**: Unique approach or clever solution
   - ✅ Reusable skill agents (not hardcoded chatbot)
   - ✅ Event-driven microservices (not monolithic)
   - ✅ System prompts layer (professional AI engineering)

2. **Technical Complexity**: Sophistication of implementation
   - ✅ Kafka + Dapr (production-grade infrastructure)
   - ✅ CI/CD automation (DevOps maturity)
   - ✅ Comprehensive testing (quality focus)

3. **Completeness**: Is it a working product?
   - ✅ All features functional (not vaporware)
   - ✅ Error handling and edge cases
   - ✅ Documentation and quickstart guide

4. **Reusability**: Can this be used again?
   - ✅ Skill agents are generic (not todo-specific)
   - ✅ Microservices are decoupled (can be reused)
   - ✅ Framework for future hackathons

5. **Presentation**: Clear communication
   - ✅ Architecture diagram
   - ✅ Live demo
   - ✅ Quick pitch (2-minute overview)

### Competitive Advantages

This Phase V architecture provides:

1. **AI-Native Foundation**: Not a wrapper around ChatGPT, but a proper AI system
2. **Production-Ready**: Not a prototype, but a deployable application
3. **Event-Driven**: Not monolithic, but microservices-based
4. **Reusable Framework**: Not one-off code, but a template for future projects
5. **Professional Engineering**: Not hacky, but follows industry best practices

### Demo Script (2 minutes)

1. **Show architecture diagram** (30 seconds)
   - Frontend → Backend → Skill Agents → Kafka → Microservices

2. **Demo basic features** (30 seconds)
   - Create task via chat: "remind me to call mom tomorrow at 5pm"

3. **Demo AI skills** (30 seconds)
   - Show how Task Agent extracts structured data from unstructured text

4. **Demo event-driven microservices** (30 seconds)
   - Show Kafka event triggering notification service

---

## Success Criteria (Phase V)

### Functional Requirements

- [ ] **Phase IV Preservation**: All Phase IV features work identically
- [ ] **Skill Agents**: All 4 required skills functional and tested
- [ ] **Event-Driven Microservices**: 3 services deployed and consuming events
- [ ] **System Prompts**: Global behavior defined and working
- [ ] **Backend Orchestrator**: Routing messages to skills correctly
- [ ] **Dapr Integration**: Pub/Sub working across all services
- [ ] **CI/CD Pipeline**: Automated deployment working

### Operational Requirements

- [ ] **Health Checks**: All services have `/health` and `/ready` endpoints
- [ ] **Resource Limits**: All pods have CPU/memory limits
- [ ] **Logging**: Structured JSON logs with correlation IDs
- [ ] **Monitoring**: Metrics exposed for Prometheus
- [ ] **Error Handling**: Retry logic, circuit breakers, graceful degradation

### Testing Requirements

- [ ] **Unit Tests**: 80%+ coverage for skill agents
- [ ] **Integration Tests**: All user journeys covered
- [ ] **Contract Tests**: All APIs and events covered
- [ ] **Smoke Tests**: Post-deployment verification

### Security Requirements

- [ ] **Secrets Management**: No hardcoded secrets
- [ ] **Input Validation**: All inputs sanitized
- [ ] **Authentication**: JWT on all protected endpoints
- [ ] **Network Security**: Kubernetes network policies

### Performance Requirements

- [ ] **Response Times**: Meet all p95 goals (< 5s for chatbot)
- [ ] **Scalability**: Can scale frontend to 10+ replicas
- [ ] **Resource Efficiency**: Cluster uses < 8 CPU cores, < 16Gi memory

---

## Golden Rules (Phase V)

### 1. No Phase IV Logic Changes
- **NO modifications** to Phase IV business logic
- All changes in orchestrator, skills, microservices
- If Phase IV features break, Phase V is **FAILED**

### 2. Skills Must Be Reusable
- **NO hardcoded todo logic** in skill agents
- Skills MUST work for any domain (tasks, emails, meetings)
- Each skill MUST have unit tests

### 3. Event-Driven Only
- **NO direct function calls** between backend and microservices
- All communication via Kafka events
- Use Dapr for pub/sub abstraction

### 4. System Prompts Are Global
- **NO skill-specific behavior** hardcoded in code
- All behavior controlled by system prompts
- Skills use system prompts + their own prompts

### 5. Production-Ready or Nothing
- **NO prototypes** or "it works on my machine"
- All services must have health checks, resource limits
- CI/CD must be fully automated

---

## Non-Functional Requirements (Phase V)

### Performance
- **Skill agent latency**: < 2 seconds (p95)
- **Backend response time**: < 1 second (p95)
- **Chatbot end-to-end**: < 5 seconds (p95)
- **Kafka event delivery**: < 100ms (p95)

### Reliability
- **Service self-healing**: Kubernetes auto-restarts failed pods
- **Event delivery**: At-least-once guarantees (Kafka + Dapr)
- **Graceful degradation**: Fallback to basic features if AI fails
- **Data persistence**: All state persisted in database

### Scalability
- **Horizontal scaling**: All services can scale to 10+ replicas
- **Event partitioning**: Kafka topics partitioned for parallelism
- **Independent scaling**: Microservices scale based on load

### Maintainability
- **Code quality**: Linting, formatting, type hints enforced
- **Documentation**: All APIs, skills, events documented
- **Testing**: Comprehensive test suite with >80% coverage
- **Debugging**: Structured logs with correlation IDs

---

## Governance

### Amendment Procedure
1. Proposal submitted as issue with rationale and impact analysis
2. Review by project architect for backward compatibility
3. Approval via pull request with migration plan for breaking changes
4. Version bump according to semantic versioning:
   - **MAJOR**: Backward incompatible changes or principle removals
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes

### Compliance Review
- All Phase V PRs MUST verify:
  - No Phase IV logic modified
  - All skill agents are reusable (not domain-specific)
  - All cross-service communication is event-driven
  - All services have health checks and resource limits
  - Tests pass (unit, integration, contract)
- Security violations MUST block merge
- Performance violations MUST be documented and justified

### Version Policy
- Current version: **5.0.0** (MAJOR - Phase V production AI principles)
- Phase III constitution locked at **3.0.0**
- Phase IV constitution locked at **4.0.0**
- Future phases will increment MINOR version (5.1.0, 5.2.0) for enhancements

### Runtime Guidance
- Use this constitution as ultimate authority for Phase V decisions
- Refer to Phase III constitution (v3.0.0) for application logic constraints
- Refer to Phase IV constitution (v4.0.0) for infrastructure constraints
- Consult `/sp.plan` outputs for architecture details
- Use skill agents for all AI capabilities

---

## Phase Definition of Done

### Phase III (Locked - Reference)
- [x] All 6 core principles implemented and validated
- [x] Qwen AI integrated via Hugging Face SDK
- [x] MCP server exposes all CRUD tools
- [x] Chat endpoint with JWT authentication functional
- [x] Conversation and Message tables deployed
- [x] Multi-language support (English + Urdu) working
- [x] User isolation verified with security tests
- [x] Stateless server architecture validated

### Phase IV (Locked - Reference)
- [x] All 11 core principles implemented (6 from Phase III + 5 new)
- [x] Repository structure created (/phase-4 with apps, infra, ai folders)
- [x] Docker images built for all services (frontend, backend, chatbot, ollama)
- [x] Helm charts generated by kubectl-ai (deployments, services, ingress)
- [x] Minikube cluster started and verified healthy
- [x] Full stack deployed via `helm install todo-app`
- [x] Frontend accessible via browser (Ingress or LoadBalancer)
- [x] Chatbot service connects to Ollama and responds to CRUD commands
- [x] kagent monitoring active and reporting cluster health
- [x] All services have resource limits and health checks
- [x] Zero-downtime rolling update tested (helm upgrade)
- [x] Phase III regression tests pass (no business logic broken)
- [x] Documentation updated (architecture diagram, runbooks, quickstart)

### Phase V (Active)
- [ ] All 18 core principles implemented (6 from Phase III + 5 from Phase IV + 7 new)
- [ ] Repository structure created (/phase-5 with agents, microservices, system_prompts)
- [ ] 4 skill agents implemented and unit tested (task, reminder, recurring, audit)
- [ ] System prompts defined (global behavior, clarification, error handling)
- [ ] Backend AI orchestrator routing messages to skills correctly
- [ ] 3 event-driven microservices deployed (notification, recurring, audit)
- [ ] Kafka + Dapr integrated and events flowing
- [ ] All services have health checks, resource limits, structured logs
- [ ] CI/CD pipeline fully automated (test → build → scan → deploy → verify)
- [ ] Test suite comprehensive (unit, integration, contract, smoke)
- [ ] Security requirements met (no hardcoded secrets, input validation, JWT auth)
- [ ] Performance requirements met (all p95 goals achieved)
- [ ] Phase IV regression tests pass (no previous features broken)
- [ ] Documentation complete (architecture, quickstart, demo script)

---

**Version**: 5.0.0 | **Ratified**: 2025-01-25 (Phase III) | **Last Amended**: 2026-02-04 (Phase V)

---

## Appendix: Quick Reference

### Phase Comparison

| Aspect | Phase III | Phase IV | Phase V |
|--------|-----------|----------|---------|
| **Focus** | AI-Native CRUD | Infrastructure | Event-Driven AI |
| **Architecture** | Monolithic | Containerized | Microservices |
| **AI** | Single chatbot | Single chatbot | Skill agents |
| **Communication** | Direct calls | Direct calls | Kafka events |
| **Scalability** | Limited | Horizontal | Independent |
| **Deployment** | Manual | Helm | CI/CD |
| **Testing** | Basic | Basic | Comprehensive |
| **Production Ready?** | No | No | Yes |

### Key Differences

**Phase IV → Phase V**:
- Chatbot → Skill agents (reusable, testable)
- Direct calls → Event-driven (decoupled)
- Manual deploy → CI/CD (automated)
- Basic logging → Structured logs (observable)
- No tests → Comprehensive tests (quality)

**What Stays The Same**:
- Phase III business logic (CRUD operations)
- Phase IV infrastructure (Kubernetes, Helm, Ollama)
- Frontend UI (no changes)

### Migration Path

**From Phase IV to Phase V**:
1. Copy `/phase-4` to `/phase-5`
2. Extract chatbot logic into skill agents
3. Add system prompts layer
4. Implement event-driven microservices
5. Integrate Kafka + Dapr
6. Add CI/CD pipeline
7. Add comprehensive tests
8. Deploy and verify

**Estimated Effort**: 2-3 days (with spec-driven approach)

---

## Appendix: Future Phases (Phase VI+)

Phase V establishes the foundation for **advanced AI capabilities**:

### Phase VI: Advanced Multi-Agent System
- **Agent Orchestration**: LangChain/AutoGen for multi-agent reasoning
- **Tool Use**: Agents can call multiple tools in sequence
- **Planning**: Agents can break down complex tasks
- **Collaboration**: Multiple agents work together (planner, executor, validator)

### Phase VII: Cloud-Native Production Deployment
- **Cloud Kubernetes**: EKS/GKE/AKS (not Minikube)
- **Managed Services**: AWS RDS, Google Cloud SQL
- **Observability**: Prometheus, Grafana, Jaeger
- **Disaster Recovery**: Multi-region deployment, backups

### Phase VIII: Advanced Features
- **RAG** (Retrieval-Augmented Generation): Vector database for knowledge base
- **Fine-tuning**: Custom LLM models for specific domains
- **Voice Interface**: Speech-to-text, text-to-speech
- **Multi-Modal**: Image and video understanding

**Rationale**: Phase V provides the production foundation. Future phases add AI sophistication and cloud scale without re-architecting the system.
