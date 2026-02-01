# Backend API Contract

**Purpose**: Document Phase III backend API endpoints for chatbot integration

**Version**: 1.0.0 (Phase III - READ-ONLY)

## Base URL

```
http://backend-service:8000
```

## Authentication

All endpoints (except `/api/health`) require JWT token in Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Health Check

```
GET /api/health
```

**Response**: 200 OK
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Create Todo

```
POST /api/todos
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high"
}
```

**Response**: 201 Created
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "completed": false,
  "user_id": 123,
  "created_at": "2026-01-30T00:00:00Z"
}
```

---

### List Todos

```
GET /api/todos
Authorization: Bearer <jwt_token>
```

**Response**: 200 OK
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "priority": "high",
      "completed": false,
      "user_id": 123,
      "created_at": "2026-01-30T00:00:00Z"
    }
  ]
}
```

---

### Get Todo by ID

```
GET /api/todos/{id}
Authorization: Bearer <jwt_token>
```

**Response**: 200 OK
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "completed": false,
  "user_id": 123,
  "created_at": "2026-01-30T00:00:00Z"
}
```

---

### Update Todo

```
PUT /api/todos/{id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, butter",
  "priority": "high",
  "completed": true
}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, butter",
  "priority": "high",
  "completed": true,
  "user_id": 123,
  "updated_at": "2026-01-30T01:00:00Z"
}
```

---

### Delete Todo

```
DELETE /api/todos/{id}
Authorization: Bearer <jwt_token>
```

**Response**: 200 OK
```json
{
  "message": "Todo deleted successfully"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

**Common Status Codes**:
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing or invalid JWT token
- 403 Forbidden - User doesn't own this todo
- 404 Not Found - Todo doesn't exist
- 500 Internal Server Error - Server error

## Chatbot Integration Notes

1. **JWT Token Forwarding**: Chatbot MUST include user's JWT token when calling backend APIs
2. **User Isolation**: Backend automatically filters todos by `user_id` from JWT
3. **Intent Mapping**:
   - "add/create/insert todo" → POST /api/todos
   - "list/show/get todos" → GET /api/todos
   - "update/edit/modify todo" → PUT /api/todos/{id}
   - "delete/remove todo" → DELETE /api/todos/{id}
4. **Priority Values**: "low", "medium", "high"
5. **Boolean Fields**: `completed` is boolean (true/false)

## Phase IV Constraint

This API contract is **READ-ONLY**. No modifications allowed in Phase IV.
