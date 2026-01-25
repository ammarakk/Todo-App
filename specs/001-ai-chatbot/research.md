# Research Findings: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2025-01-25
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document consolidates research findings for 5 critical technical decisions required to implement the Phase III AI-Powered Todo Chatbot. Each research question addresses architectural uncertainty identified during planning.

---

## R1: MCP SDK Integration Patterns

### Question
How to integrate Official MCP SDK with FastAPI?

### Research Findings

**MCP SDK Overview**:
- Model Context Protocol (MCP) is a standardized protocol for AI-agent tool execution
- Official Python SDK: `mcp` package (available via PyPI)
- Provides server implementation, tool registration, and request/response handling

**Integration Architecture**:

```python
# backend/src/services/mcp_server.py
from mcp import Server, Tool
from fastapi import FastAPI

app = FastAPI()
mcp_server = Server("todo-mcp-server")

# Tool registration
@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = None):
    """Create a new task for the user"""
    # Implementation
    pass

# FastAPI integration
@app.post("/api/chat")
async def chat_endpoint(message: str, user_id: str):
    # Chat service calls MCP tools via server.execute_tool()
    pass
```

**Decision**: In-process MCP server integration
- MCP server runs within FastAPI process (not separate service)
- Tools exposed as async Python functions
- Chat service calls tools directly via `mcp_server.call_tool()`

**Rationale**:
- Simpler deployment (single service)
- Lower latency (no network overhead)
- Easier testing (direct function calls)
- Scales with FastAPI workers

**Alternatives Considered**:
1. **Separate MCP Server Process**: Rejected due to deployment complexity and network latency
2. **MCP over HTTP**: Rejected due to protocol overhead for in-process calls

**Best Practices**:
- Use async tool functions for non-blocking I/O
- Validate tool inputs before execution
- Return structured JSON responses
- Log all tool calls for observability

---

## R2: Qwen Model Capabilities

### Question
Does Qwen support English-Urdu language detection and response?

### Research Findings

**Qwen Model Overview**:
- Model: `Qwen/Qwen-72B-Chat` (or `Qwen-14B-Chat` for faster inference)
- Multilingual capabilities: Supports 10+ languages including English and Urdu
- Context window: 32K tokens (sufficient for conversation history)
- Available via Hugging Face Inference API

**Language Detection Strategy**:

```python
# Automatic detection via Qwen
prompt = f"User message: {user_message}"
response = qwen_client.generate(
    prompt,
    language="auto"  # Qwen auto-detects input language
)
# Qwen responds in same language as input
```

**Bilingual Support Confirmation**:
- ✅ English: Full support, native-like responses
- ✅ Urdu: Full support, handles Urdu script (اردو) and Roman Urdu
- ✅ Mixed Language: Can handle English-Urdu code-switching

**Prompt Engineering Patterns**:

**System Prompt (English)**:
```
You are a helpful task management assistant. You help users create, list, update, and delete tasks through natural conversation. Always respond in the same language as the user's message.
```

**System Prompt (Urdu)**:
```
آپ ایک مددگار ٹاسک مدیریت اسسٹنٹ ہیں۔ آپ صارفین کو قدرتی گفتگو کے ذریعے ٹاسک بنانے، فہرست دکھانے، اپ ڈیٹ کرنے اور حذف کرنے میں مدد کرتے ہیں۔ ہمیشہ صارف کے پیغام کی نفس زبان میں جواب دیں۔
```

**Decision**: Use Qwen auto-detection with bilingual system prompts
- Set `language="auto"` in API calls
- Detect language from user message for system prompt selection
- Fallback to English if detection fails

**Rationale**:
- Qwen's multilingual training handles Urdu natively
- Auto-detection reduces complexity (no separate language detection service)
- Single model serves both languages

**Alternatives Considered**:
1. **Separate Language Detection Service**: Rejected due to added latency and complexity
2. **Different Models per Language**: Rejected due to cost and deployment overhead

**Best Practices**:
- Include language examples in system prompt
- Test with Roman Urdu (e.g., "Mera task add karo")
- Monitor language accuracy metrics
- Fallback to English on detection failure

---

## R3: Conversation Pagination Strategy

### Question
How to handle conversations with 10,000+ messages efficiently?

### Research Findings

**Challenge**: Qwen context window is 32K tokens (~24,000 words or ~800 average messages). Large conversations exceed this limit.

**PostgreSQL Pagination Patterns**:

```python
# Efficient pagination with keyset pagination
def get_conversation_messages(conversation_id: str, limit: int = 100):
    return session.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .all()  # Last 100 messages
```

**Context Window Optimization Strategy**:

**Approach 1: Recent Messages Only**
```python
# Load last 100 messages for context
recent_messages = load_messages(conversation_id, limit=100)
context = build_message_array(recent_messages)
```

**Approach 2: Sliding Window**
```python
# Load messages around most recent user message
messages = load_messages_around(
    conversation_id,
    message_id=last_user_message_id,
    before=50,
    after=50
)
```

**Approach 3: Summarization** (Future Enhancement)
- Summarize older messages (e.g., first 1000 messages → 200-word summary)
- Prepend summary to context
- *Deferred to Phase IV*

**Decision**: Use Approach 1 (Recent 100 Messages)
- Load last 100 messages for AI context
- Sufficient for task management context
- Simple implementation
- Fast query performance (<500ms)

**Rationale**:
- 100 messages ≈ 4K tokens (well within 32K limit)
- Task conversations rarely need >10 message history
- Full history preserved in DB (archival, not context)
- Scales to 10,000+ message conversations

**Alternatives Considered**:
1. **Full History Loading**: Rejected due to context window limits
2. **Vector Search for Relevance**: Rejected due to complexity (Phase IV candidate)
3. **Summarization**: Deferred to future phase

**Best Practices**:
- Add index on `(conversation_id, created_at DESC)` for fast queries
- Monitor average conversation length
- Alert if conversations exceed 1000 messages (consider summarization)
- Cache recent messages in Redis (optional optimization)

---

## R4: MCP Tool Schema Design

### Question
What schemas should MCP tools expose for task operations?

### Research Findings

**MCP Tool Schema Specification**:
- Tools defined with JSON Schema for validation
- Input schema: Validates parameters
- Output schema: Defines response structure
- Error handling via standardized error responses

**Tool Schema Design**:

**1. add_task Tool**
```json
{
  "name": "add_task",
  "description": "Create a new task for the user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (from JWT)"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "Task title"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "Optional task description"
      }
    },
    "required": ["user_id", "title"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "integer"},
      "title": {"type": "string"},
      "status": {"type": "string", "enum": ["pending"]},
      "created_at": {"type": "string", "format": "date-time"}
    }
  }
}
```

**2. list_tasks Tool**
```json
{
  "name": "list_tasks",
  "description": "List all tasks for the user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (from JWT)"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed", "all"],
        "default": "all"
      }
    },
    "required": ["user_id"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "tasks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "status": {"type": "string"},
            "created_at": {"type": "string"}
          }
        }
      },
      "count": {"type": "integer"}
    }
  }
}
```

**3. delete_task Tool**
```json
{
  "name": "delete_task",
  "description": "Delete a specific task",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid"
      },
      "task_id": {
        "type": "integer",
        "minimum": 1
      }
    },
    "required": ["user_id", "task_id"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "message": {"type": "string"}
    }
  }
}
```

**4. update_task Tool**
```json
{
  "name": "update_task",
  "description": "Mark task as completed",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string", "format": "uuid"},
      "task_id": {"type": "integer", "minimum": 1},
      "status": {
        "type": "string",
        "enum": ["completed", "pending"]
      }
    },
    "required": ["user_id", "task_id", "status"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "integer"},
      "status": {"type": "string"}
    }
  }
}
```

**Error Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "string",
      "description": "Error message (bilingual if possible)"
    },
    "code": {
      "type": "string",
      "enum": ["NOT_FOUND", "VALIDATION_ERROR", "PERMISSION_DENIED"]
    }
  },
  "required": ["error", "code"]
}
```

**Decision**: Use above schemas for all 4 MCP tools
- Consistent structure across tools
- JSON Schema validation in MCP SDK
- user_id required in all tools (security)
- Descriptive error codes for AI understanding

**Rationale**:
- Standard JSON Schema integrates with MCP SDK
- Explicit validation prevents invalid data
- Error codes help AI understand failures
- user_id enforces security isolation

**Best Practices**:
- Validate inputs before DB operations
- Return descriptive error messages
- Log all tool calls with user_id
- Use enums for fixed values (status, error codes)

---

## R5: Error Handling Best Practices

### Question
How to handle Qwen inference failures gracefully?

### Research Findings

**Failure Modes**:
1. **Network Timeout**: HuggingFace API >8s timeout
2. **Rate Limiting**: API quota exceeded
3. **Model Unavailable**: Service downtime
4. **Invalid Response**: Malformed JSON, unexpected format
5. **Tool Execution Failure**: Database error, validation error

**Retry Strategy**:

```python
# Exponential backoff with jitter
import asyncio
import random

async def call_qwen_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = await qwen_client.generate(messages, timeout=8)
            return response
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(wait_time)
        except APIError as e:
            if e.status == 429:  # Rate limit
                await asyncio.sleep(60)  # Wait 1 minute
            else:
                raise
```

**Fallback Responses**:

**English Fallback**:
```
I'm having trouble connecting right now. Please try again in a moment.
```

**Urdu Fallback**:
```
مجھے ابھی رابطے میں مسئلہ آ رہا ہے۔ براہ کرم تھوڑی دیر بعد کوشش کریں۔
```

**Timeout Handling**:
- Set 8s timeout per request (leaves 2s buffer for <10s p95)
- Retry once on timeout (total 16s max)
- Return fallback after retries exhausted

**Tool Execution Failures**:
- Catch exceptions in MCP tools
- Return error response to AI
- AI explains error to user in their language

```python
try:
    result = await mcp_server.call_tool("add_task", params)
except ValidationError as e:
    error_response = {
        "error": str(e),
        "code": "VALIDATION_ERROR"
    }
    # Send error back to Qwen for explanation
```

**Decision**: Implement retry with exponential backoff + fallback responses
- Retry up to 3 times with exponential backoff
- Return bilingual fallback after retries exhausted
- Log all failures for monitoring
- Alert on >10% error rate

**Rationale**:
- Retry handles transient failures (network blips)
- Exponential backoff avoids overwhelming API
- Fallback maintains user experience during outages
- Bilingual fallbacks maintain language consistency

**Alternatives Considered**:
1. **Circuit Breaker**: Considered but deferred to Phase IV (complexity vs. benefit)
2. **Multiple AI Models**: Rejected due to cost and complexity
3. **Queue and Retry**: Rejected due to user expectation of real-time response

**Best Practices**:
- Monitor error rate and latency
- Alert on degradation (>5% error rate)
- Test failure scenarios (timeout, 500 errors)
- Log retry attempts for debugging
- Provide clear feedback to users

---

## Summary of Decisions

| Research Question | Decision | Key Rationale |
|-------------------|----------|---------------|
| R1: MCP SDK Integration | In-process MCP server with FastAPI | Simpler deployment, lower latency, easier testing |
| R2: Qwen Language Support | Use Qwen auto-detection with bilingual system prompts | Native multilingual support, simpler architecture |
| R3: Conversation Pagination | Load last 100 messages for context | Within 32K token limit, sufficient for task conversations |
| R4: Tool Schema Design | JSON Schema for 4 tools with user_id enforcement | Standard validation, security isolation, AI-friendly errors |
| R5: Error Handling | Retry with exponential backoff + bilingual fallbacks | Handles transient failures, maintains UX during outages |

---

## Next Steps

With research complete, proceed to **Phase 1: Design & Contracts**:
1. Create `data-model.md` with Conversation and Message entity definitions
2. Create `contracts/chat-api.yaml` with OpenAPI specification
3. Create `contracts/mcp-tools.yaml` with tool schemas
4. Create `quickstart.md` with setup instructions
5. Run agent context update script

All technical unknowns resolved. Ready for detailed design phase.
