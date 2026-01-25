# speckit.specify

**Phase III – AI Todo Chatbot**

## 1. User Journeys

### 1.1 Add Task

User can say:

* "Add a task to buy milk"
* "Doodh lene ka task add karo"

AI must:

* Call MCP `add_task`
* Confirm in the same language

---

### 1.2 List Tasks

User can say:

* "Show my tasks"
* "Mere tasks dikhao"

AI must:

* Call MCP `list_tasks`
* Show only this user's data

---

### 1.3 Delete Task

User can say:

* "Delete task 3"
* "Task number 3 hata do"

AI must:

* Verify ownership
* Call MCP `delete_task`
* Confirm deletion

---

### 1.4 Mark Complete

User can say:

* "Mark task 1 as done"
* "Pehla task complete karo"

AI must:

* Call MCP `update_task`
* Confirm in the same language

---

## 2. Acceptance Criteria

| Area       | Rule                   |
| ---------- | ---------------------- |
| Language   | Reply in same language |
| Validation | Title 1–200 chars      |
| Errors     | Friendly messages      |
| Security   | JWT-isolated user data |
| Memory     | Conversations persist  |

---

## 3. Domain Rules

* Every message reloads conversation from Neon
* No MCP call without `user_id`
* No silent failures
* Deterministic behavior

---

## 🚀 Next Command

Run in Claude:

```
Read @speckit.constitution
Read @speckit.specify

Now generate Phase III
/sp.plan
```
