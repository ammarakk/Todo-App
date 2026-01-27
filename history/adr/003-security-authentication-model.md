# ADR-003: Security and Authentication Model

**Status**: Accepted
**Date**: 2026-01-27
**Context**: Phase 3 AI Assistant Integration

---

## Context

The AI Assistant processes user commands and manipulates Todo data, creating significant security risks:
- AI could be tricked into accessing other users' tasks
- Malicious input could attempt injection attacks
- Unauthenticated access could expose private data
- Direct database access could bypass security layers

**Constitutional Requirements**:
- **Principle IV**: Strict Security & User Isolation - "AI agent is STRICTLY PROHIBITED from accessing or modifying any task that does not belong to the authenticated user_id"
- **All database queries MUST include user_id filters**
- **JWT verified on every request**

**User Requirements**:
- 100% of AI operations must maintain authentication (SC-006)
- AI can only access/modify user's own tasks
- Input sanitization required (FR-023)

---

## Decision

**Defense-in-depth security architecture with JWT as the single source of truth for user identity**.

**Implementation Components**:

1. **Authentication Enforcement**:
   ```python
   # All AI endpoints require JWT
   async def ai_command_endpoint(
       request: AICommandRequest,
       current_user: User = Depends(get_current_user)  # JWT validation
   ):
       # current_user.id used for ALL operations
       pass
   ```

2. **User Identity Extraction**:
   - `user_id` extracted from JWT token **ONCE** at endpoint entry
   - `user_id` passed to all downstream operations (never from AI or user input)
   - AI never receives `user_id` in prompts or can control it

3. **MCP Tool User Isolation**:
   ```python
   async def create_todo_tool(title: str, user_id: UUID):  # user_id from JWT
       # Query ALWAYS includes user_id filter
       todo = Todo(title=title, user_id=user_id)
       # Database query: WHERE user_id = ?
   ```

4. **Input Sanitization**:
   - All user messages sanitized **before** sending to Qwen
   - Remove HTML tags, SQL patterns, XSS attempts
   - Validate message length and character set

5. **No Direct Database Access**:
   - AI only interacts through MCP tools
   - MCP tools call existing Todo APIs (which already have security)
   - Double protection: MCP layer + API layer

6. **Fail-Safe Defaults**:
   - All endpoints require authentication (no public AI endpoints)
   - Reject invalid/expired JWTs with 401 Unauthorized
   - Log all security violations (failed auth, isolation breaches)

---

## Alternatives Considered

1. **Pass user_id from Frontend to AI**
   - **Pros**: Simpler, no JWT dependency in AI logic
   - **Cons**: **CRITICAL SECURITY FLAW** - User can spoof other user IDs
   - **Rejected**: User isolation completely broken

2. **Let AI Extract user_id from Context**
   - **Pros**: AI more "aware" of user context
   - **Cons**: AI could be manipulated to return different user_id
   - **Rejected**: AI is untrusted component for security decisions

3. **Separate Authentication for AI Endpoints**
   - **Pros**: Different security levels for different endpoints
   - **Cons**: More complex, inconsistent, harder to maintain
   - **Rejected**: Single authentication source simpler and more secure

4. **Store user_id in Conversation Table**
   - **Pros**: Easy to filter conversations by user
   - **Cons**: **Insufficient** - still need JWT validation per request
   - **Rejected**: Storage doesn't replace authentication

5. **Relaxed Input Sanitization (Trust AI)**
   - **Pros**: Faster, no preprocessing
   - **Cons**: **XSS and SQL injection risks**, AI can be tricked
   - **Rejected**: Security vulnerability

---

## Consequences

**Positive**:
- **Strong User Isolation**: Impossible for AI to access other users' tasks (user_id from immutable JWT)
- **Defense-in-Depth**: JWT → MCP tools → Todo APIs (three security layers)
- **Compliance Ready**: Meets common security standards (OWASP)
- **Audit Trail**: All AI operations tied to authenticated user_id in logs
- **Testable Security**: Clear security boundaries for testing

**Negative**:
- **JWT Dependency**: AI completely unavailable if JWT service fails (acceptable - fail-closed)
- **Performance Overhead**: JWT validation on every request (<5ms, acceptable)
- **Strict Enforcement**: No "anonymous AI" mode possible (by design for this application)
- **Input Validation Overhead**: Sanitization adds processing time (<1ms, acceptable)

**Neutral**:
- **Session-Based**: Uses existing Phase 2 JWT sessions (no new auth system)
- **User Scope**: All operations scoped to authenticated user (no multi-user AI conversations)
- **Logging**: All commands logged with user_id for monitoring

---

## References

- [plan.md](../specs/001-ai-assistant/plan.md) - Section 2.3 Security Architecture
- [spec.md](../specs/001-ai-assistant/spec.md) - Security Requirements (FR-013, FR-023, SC-006)
- Constitution Principle IV: Strict Security & User Isolation
- OWASP Top 10: Authentication and Authorization
- Success Criterion SC-006: "100% of AI operations maintain authentication"

---
