# ADR-002: AI Communication and Data Flow Architecture

**Status**: Accepted
**Date**: 2026-01-27
**Context**: Phase 3 AI Assistant Integration

---

## Context

The AI Assistant needs to process natural language commands, execute Todo operations, and return results to the user. The key challenge was designing a communication flow that:
- Maintains stateless server architecture (constitutional requirement)
- Reuses existing Phase 2 infrastructure (Qwen, MCP, Todo APIs)
- Provides acceptable performance (<3s response time p95)
- Ensures security and user isolation
- Avoids duplicating CRUD logic

**Constraints from Plan**:
- AI must NOT directly access the database
- AI must use existing Todo APIs
- Server must be stateless (conversation history in database)
- MCP tools are the only interface for AI operations

---

## Decision

**Layered architecture with HTTP polling for communication** and strict separation of concerns.

**Implementation Components**:

1. **Request Flow**:
   ```
   User Message (Dashboard)
       ↓
   POST /api/ai-command (JWT validated)
       ↓
   Load conversation history from DB
       ↓
   Build message array (Qwen format)
       ↓
   Call Qwen API (qwen_client.py)
       ↓
   Parse AI response (action + parameters)
       ↓
   Validate action
       ↓
   Execute via MCP tools → calls existing Todo APIs
       ↓
   Save messages to Conversation/Message tables
       ↓
   Return formatted response to Dashboard
   ```

2. **Communication Protocol**: **Simple HTTP with polling** (not SSE/WebSocket)
   - Frontend polls every 1 second or re-fetches after action completion
   - AI returns complete responses (no streaming)

3. **MCP Tool Integration**:
   - AI ONLY interacts through MCP tools (no direct DB access)
   - MCP tools call existing Todo APIs (`todos.py`)
   - Tools: `create_todo`, `list_todos`, `update_todo`, `delete_todo`, `complete_todo`

4. **Performance Optimizations**:
   - **Conversation History Pagination**: Load last 50 messages on panel open
   - **In-Memory Caching**: Cache active conversation per user
   - **Async Processing**: Non-blocking AI requests with loading indicators

5. **Error Handling Strategy**:
   - AI service failure → Friendly error + suggest manual UI
   - Invalid action → AI asks clarifying question
   - Database error → Log + return error message
   - Timeout → "AI unavailable" message

---

## Alternatives Considered

1. **Server-Sent Events (SSE) for Streaming**
   - **Pros**: True real-time streaming, character-by-character AI responses, no polling overhead
   - **Cons**: Significantly more complex, harder to test, requires connection management, overkill for <3s targets
   - **Rejected**: Polling simpler and sufficient for performance requirements

2. **WebSocket Connection**
   - **Pros**: Bidirectional real-time, efficient for high-frequency updates
   - **Cons**: Complex connection lifecycle, harder to scale, stateful connections, debugging difficulty
   - **Rejected**: Adds complexity without clear benefit for low-volume chat

3. **Direct Database Access from AI**
   - **Pros**: Faster, bypasses API layer, simpler data flow
   - **Cons**: Breaks security boundaries, duplicates validation logic, violates constitutional MCP-first principle
   - **Rejected**: Security risk, violates Principle VI (MCP-First Tool Design)

4. **No Conversation History (Stateless Chat)**
   - **Pros**: Simpler, no database storage, faster
   - **Cons**: No context continuity, poor UX, violates Principle III (Persistence of Intelligence)
   - **Rejected**: Constitution requires conversation persistence

5. **Synchronous AI Requests (Blocking)**
   - **Pros**: Simpler error handling
   - **Cons**: Blocks server, poor scalability, bad UX during processing
   - **Rejected**: Performance target (<3s p95) requires async

---

## Consequences

**Positive**:
- **Clean Separation of Concerns**: Each layer has single responsibility (API → AI → MCP → Todo)
- **Security by Design**: AI cannot bypass validation, user_id enforced at MCP layer
- **Reusability**: Leverages existing Qwen, MCP tools, and Todo APIs
- **Stateless Server**: Easy horizontal scaling, no session state in memory
- **Testability**: Each layer can be tested independently
- **Performance**: Async + caching + pagination meets <3s p95 target

**Negative**:
- **Polling Overhead**: 1-second polling adds background requests (mitigated by low volume)
- **No True Streaming**: Users don't see character-by-character responses (acceptable for <3s latency)
- **Layer Indirection**: AI → MCP → Todo API adds call overhead (acceptable for simplicity)
- **Memory Cache**: Requires cache invalidation strategy on new messages

**Neutral**:
- **Conversation Pagination**: Users see last 50 messages (reasonable for task management)
- **One Active Conversation**: Simpler state management vs multiple conversations

---

## References

- [plan.md](../specs/001-ai-assistant/plan.md) - Section 2.2 Backend Architecture
- [plan.md](../specs/001-ai-assistant/plan.md) - Section 2.4 Performance Architecture
- Constitution Principle II: Stateless Server Architecture
- Constitution Principle VI: MCP-First Tool Design
- Constitution Principle III: Persistence of Intelligence
- User requirement: "AI must never access database directly"

---
