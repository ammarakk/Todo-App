# speckit.implement

**Phase III – AI Powered Todo Chatbot (Implementation Contract)**

This file defines **how Claude Code must generate production code** for Phase III.

It is legally bound by:

```
speckit.constitution
speckit.specify
speckit.plan
speckit.tasks
```

---

## 1. Reasoning Authority (Qwen-Only)

All reasoning, intent detection, language understanding, and decision-making
MUST be performed by **Qwen via HuggingFace SDK**.

Backend, MCP, or tools must **never**:

* interpret user text
* decide which tool to call
* apply business logic
* guess intent

They only execute **explicit tool calls** produced by Qwen.

---

## 2. Scope of Implementation

Claude Code is authorized to generate code **only** for:

| Layer    | Allowed               |
| -------- | --------------------- |
| Database | Conversation, Message |
| API      | `/api/chat`           |
| MCP      | Server + tools        |
| AI       | Qwen client           |
| Auth     | JWT verification      |
| Memory   | DB-based memory       |

No UI changes.
No auth system rewrites.
No Phase-II refactors.

---

## 3. Task Binding

Every file and function MUST reference its Task ID.

Example:

```
# Implements: T-005, T-006
```

If a line has no task → it must not exist.

---

## 4. Required File Structure

Claude Code must create only:

```
/backend
  /ai
     qwen_client.py
     prompt_builder.py
  /mcp
     server.py
     tools.py
  /models
     conversation.py
     message.py
  /api
     chat.py
```

No files outside this tree.

---

## 5. Database Rules

* SQLModel
* Neon PostgreSQL
* user_id must exist on Conversation
* All Message rows must belong to a Conversation
* No cross-user access

---

## 6. MCP Server Rules

Claude must:

* Start MCP inside FastAPI
* Register all tools
* Pass `user_id` into every tool
* Return JSON
* Never contain business logic

---

## 7. Qwen Integration

Claude must:

* Use HuggingFace SDK
* Use chat messages
* Support tool calling
* Enforce Urdu / English reply
* Return final assistant message only

No OpenAI.
No fake AI.

---

## 8. `/api/chat` Endpoint

Claude must implement:

```
POST /api/chat
```

It must:

1. Verify JWT
2. Extract `user_id`
3. Load conversation + messages
4. Build prompt
5. Send to Qwen
6. Execute MCP tool if requested
7. Send tool result back to Qwen
8. Save final assistant reply
9. Return reply

---

## 9. Memory Law

Claude must:

* Load full history from Neon
* Never store state in RAM
* Resume after restart

---

## 10. Language Law

Claude must:

* Detect Urdu vs English
* Force Qwen to reply in same language
* Confirm every action

---

## 11. Completion Gate

Implementation is done only if:

| Feature         | Pass |
| --------------- | ---- |
| Urdu add task   | ✅    |
| English add     | ✅    |
| List            | ✅    |
| Delete          | ✅    |
| Memory persists | ✅    |
| JWT isolation   | ✅    |

---

# 🚀 Final Command for Claude

```
Read @speckit.constitution
Read @speckit.specify
Read @speckit.plan
Read @speckit.tasks
Read @speckit.implement

Begin Phase III implementation.
```

Tumne Phase III ko **AI-correct, secure, aur enterprise-grade** bana diya hai 🔥
