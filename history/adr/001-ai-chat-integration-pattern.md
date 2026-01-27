# ADR-001: AI Chat Integration Pattern

**Status**: Accepted
**Date**: 2026-01-27
**Context**: Phase 3 AI Assistant Integration

---

## Context

Phase 2 Todo system was functional with a standalone chatbot page at `/chat`. This created a disconnected UX where users had to navigate away from their tasks to interact with AI. The requirement was to integrate AI as a control interface layer that enhances task management without rebuilding or duplicating Phase 2 functionality.

**Key Constraints**:
- AI must be an integration layer, not a separate application
- Zero regression in Phase 2 Todo functionality
- AI should be always accessible while using the Dashboard
- Must maintain existing authentication and user isolation

---

## Decision

**Integrate AI Assistant as a floating chat panel within the Dashboard** instead of a standalone page.

**Implementation Components**:
- **UI Pattern**: Fixed bottom-right floating button that expands into a modal chat panel
- **Component Architecture**:
  - `AIChatButton`: Floating action button (always visible)
  - `AIChatPanel`: Modal/panel container (dismissable, re-openable)
  - `ChatMessage`: Individual message display with role styling
  - `ChatInput`: Text input field with send button
  - `useAIChat`: React hook for chat state management
- **State Management**: React Context (`AIChatContext`) for centralized chat state
- **Persistence**: Conversation ID stored in localStorage for session continuity
- **Dashboard Synchronization**: After AI executes task action, trigger re-fetch of Todo list to show changes
- **Real-time Updates**: Polling at 1-second interval or re-fetch after action completion

**Key Design Principle**: AI is an **overlay control layer** - it manipulates the Todo system but does not duplicate it.

---

## Alternatives Considered

1. **Standalone Chatbot Page** (existing implementation)
   - **Pros**: Simpler implementation, clearer separation of concerns
   - **Cons**: Poor UX (navigation away from tasks), no real-time visual feedback, violates "integration layer" principle
   - **Rejected**: User explicitly required unified application

2. **Sidebar Chat Interface**
   - **Pros**: Always visible, more screen space for chat
   - **Cons**: Reduces Dashboard workspace, more invasive, clutters UI on smaller screens
   - **Rejected**: Less flexible than floating panel, doesn't follow productivity app patterns

3. **Inline Chat Within Todo List**
   - **Pros**: Tightest integration with tasks
   - **Cons**: Noisy interface, hard to focus, confuses task management with AI conversation
   - **Rejected**: Mixing concerns reduces usability for both tasks and AI

4. **Server-Sent Events (SSE) or WebSocket**
   - **Pros**: True real-time streaming responses
   - **Cons**: Significantly more complex, harder to test, over-engineered for <3s response targets
   - **Rejected**: Polling + HTTP responses sufficient, simpler implementation

---

## Consequences

**Positive**:
- **Unified UX**: Users see AI manipulate tasks in real-time without leaving Dashboard
- **Always Accessible**: Floating button provides instant access from any Dashboard view
- **Non-Intrusive**: Panel can be dismissed when not needed
- **Proven Pattern**: Follows successful productivity apps (Intercom, Crisp, Drift)
- **Simpler Implementation**: No SSE/WebSocket complexity, easier to test and debug
- **Zero Regression**: Phase 2 Todo UI remains completely intact

**Negative**:
- **State Synchronization Complexity**: Must coordinate AI changes with Dashboard state (re-fetch after actions)
- **Polling Overhead**: 1-second polling adds background load (mitigated by low message volume)
- **Not True Streaming**: Users don't see character-by-character AI responses (acceptable for <3s targets)
- **UI State Management**: React Context + localStorage adds frontend complexity

**Neutral**:
- **Session-Scoped History**: Conversations persist per session but not across browser sessions (by design)
- **Single Conversation**: One active conversation per user (simplifies state management)

---

## References

- [spec.md](../specs/001-ai-assistant/spec.md) - User Stories 1-3 (P1-P3)
- [plan.md](../specs/001-ai-assistant/plan.md) - Section 2.1 Frontend Architecture
- Constitution Principle I: AI-Native Interaction (chatbot as primary interface)
- User requirement: "AI must NOT exist as a separate page or route"

---
