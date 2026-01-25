# speckit.constitution

**Phase III – AI-Powered Todo Brain**

## 1. Core Mission (WHY)

This system must transform the Todo App into a **secure, conversational, persistent AI system** where users manage their tasks using natural language.

The AI is not a chatbot.
It is a **private AI task operator** for each user.

---

## 2. Technology Lock (Non-Negotiable)

| Layer          | Technology                 |
| -------------- | -------------------------- |
| LLM            | Qwen (HuggingFace SDK)     |
| Agent Protocol | Official MCP SDK           |
| Database       | Neon Serverless PostgreSQL |
| Backend        | FastAPI + SQLModel         |
| Auth           | JWT (FastAPI native)       |
| Frontend       | Existing Next.js           |

No BetterAuth.
No OpenAI.
No in-memory state.

---

## 3. Architecture Laws

### 3.1 Stateless Server

The backend must store **zero session or AI memory in RAM**.

Every request:

* verifies JWT
* loads conversation + messages from Neon
* builds the AI prompt

This guarantees:

* crash safety
* horizontal scaling
* no hallucinated memory

---

### 3.2 Persistent Intelligence

All conversations and AI messages must be stored in:

```
Conversation
Message
```

The AI must remember:

* what the user said
* what tasks exist
* previous replies

even after restarts.

---

### 3.3 Tool-Only Execution

The AI is forbidden from directly touching the database.

All actions must go through **MCP tools**:

* add_task
* list_tasks
* delete_task
* update_task

This prevents hallucinated writes.

---

## 4. Security & User Isolation

Every request must:

1. Validate JWT
2. Extract `user_id`
3. Pass `user_id` into MCP tools

The AI is never allowed to:

* see another user's tasks
* delete another user's data
* infer hidden IDs

---

## 5. Language Law

The AI must:

* Accept Urdu & English
* Reply in the same language
* Always confirm actions politely

---

## 6. Spec-Driven Law

Hierarchy of truth:

```
Constitution > Specify > Plan > Tasks > Code
```

No code without a Task ID.
Claude Code is the only system allowed to implement.
