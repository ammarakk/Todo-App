"""
Chatbot Service - Phase IV with Gordon Agent Integration
FastAPI service using cagent (Gordon) for NLP instead of Qwen
"""
from fastapi import FastAPI, WebSocket, HTTPException, Header, WebSocketDisconnect
from pydantic import BaseModel
import httpx
import os
import logging
import subprocess
import json
import re
from typing import Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gordon Todo Chatbot Service", version="2.0.0")

# Environment variables
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend-service:8000")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

if not QWEN_API_KEY:
    logger.warning("QWEN_API_KEY not set. Qwen API will not work!")


class ChatRequest(BaseModel):
    message: str
    user_token: Optional[str] = None


class GordonAgent:
    """Hybrid Agent: Qwen API with Ollama fallback"""

    QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://todo-ollama:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

    @staticmethod
    async def parse_message(message: str) -> dict:
        """
        Parse user message into structured todo action
        Tries Qwen API first, falls back to Ollama if unavailable
        Returns: {"action": "CREATE/DELETE/LIST/UPDATE", "data": {...}}
        """
        prompt = f"""You are a todo task manager. Parse user messages and extract the action.

ONLY output valid JSON. No other text or explanations.

Actions:
1. CREATE: User wants to add/create/make a new todo
   Keywords: "task", "todo", "add", "create", "remind", "urgent", "important"
   Output: {{"action": "CREATE", "todos": [{{"title": "task description", "priority": "HIGH/MEDIUM/LOW"}}]}}

2. DELETE: User wants to remove/delete a todo
   Keywords: "delete", "remove", "forget", "erase"
   Output: {{"action": "DELETE", "title": "task name"}}

3. LIST: User wants to see/list their todos
   Keywords: "show", "list", "get", "my tasks", "all todos"
   Output: {{"action": "LIST"}}

4. UPDATE: User wants to mark a todo as complete or change it
   Keywords: "mark done", "complete", "finish", "update"
   Output: {{"action": "UPDATE", "title": "task name", "status": "completed"}}

Priority detection rules:
- "urgent", "important", "critical" → HIGH
- "soon", "later" → MEDIUM
- Default → LOW

Examples:

Input: "urgent task fix the bug"
Output: {{"action": "CREATE", "todos": [{{"title": "fix the bug", "priority": "HIGH"}}]}}

Input: "add task buy milk"
Output: {{"action": "CREATE", "todos": [{{"title": "buy milk", "priority": "LOW"}}]}}

Input: "delete task buy milk"
Output: {{"action": "DELETE", "title": "buy milk"}}

Input: "show my tasks"
Output: {{"action": "LIST"}}

Input: "mark done call mom"
Output: {{"action": "UPDATE", "title": "call mom", "status": "completed"}}

Remember: ONLY return valid JSON, no markdown, no code blocks, no explanations.

User message: {message}

Output:"""

        def extract_json(output: str) -> dict:
            """Extract JSON from LLM output"""
            # Try to find JSON with "action" key
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', output, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            # Try parsing entire output as JSON
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # If model outputs Chinese wrapper, try to extract English JSON
                if '操作成功' in output or '"code"' in output:
                    # Model returned API response format instead of pure JSON
                    # Fallback to rule-based extraction
                    return None
                return None

        def rule_based_parse(message: str) -> dict:
            """Simple rule-based parser as final fallback"""
            msg_lower = message.lower().strip()

            # LIST
            if any(word in msg_lower for word in ['show', 'list', 'get my', 'all todos', 'my tasks']):
                return {"action": "LIST"}

            # DELETE
            if any(word in msg_lower for word in ['delete', 'remove']):
                # Extract title after the keyword
                for keyword in ['delete ', 'remove ']:
                    if keyword in msg_lower:
                        title = msg_lower.split(keyword)[1].strip()
                        return {"action": "DELETE", "title": title}
                return {"action": "DELETE", "title": message.split()[-1]}

            # UPDATE / MARK DONE
            if any(word in msg_lower for word in ['mark done', 'complete', 'finish']):
                # Extract title
                for keyword in ['mark done ', 'done ', 'complete ', 'finish ']:
                    if keyword in msg_lower:
                        title = msg_lower.split(keyword)[1].strip()
                        return {"action": "UPDATE", "title": title, "status": "completed"}
                return {"action": "UPDATE", "title": message.split()[-1], "status": "completed"}

            # CREATE (default)
            # Determine priority
            priority = "LOW"
            if any(word in msg_lower for word in ['urgent', 'important', 'critical']):
                priority = "HIGH"
            elif any(word in msg_lower for word in ['soon', 'later']):
                priority = "MEDIUM"

            # Extract title - remove common keywords
            title = msg_lower
            for keyword in ['task ', 'todo ', 'add ', 'create ', 'make ', 'urgent ', 'important ']:
                if keyword in title:
                    title = title.replace(keyword, '', 1)
            title = title.strip() or message

            return {"action": "CREATE", "todos": [{"title": title, "priority": priority}]}

        # Try Qwen API first
        if QWEN_API_KEY:
            try:
                logger.info(f"Trying Qwen API with message: {message[:100]}...")
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        f"{GordonAgent.QWEN_API_URL}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {QWEN_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "qwen-plus",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0,
                            "max_tokens": 512
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        output = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        logger.info(f"Qwen raw output: {output[:500]}")
                        parsed = extract_json(output)
                        if parsed:
                            logger.info(f"Parsed intent from Qwen: {parsed}")
                            return parsed
                    else:
                        logger.warning(f"Qwen API returned {response.status_code}, trying Ollama fallback")
            except Exception as e:
                logger.warning(f"Qwen API failed: {e}, trying Ollama fallback")

        # Fallback to Ollama
        try:
            logger.info(f"Using Ollama with message: {message[:100]}...")
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{GordonAgent.OLLAMA_API_URL}/api/generate",
                    json={
                        "model": GordonAgent.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0}
                    }
                )

                if response.status_code == 200:
                    output = response.json().get("response", "").strip()
                    logger.info(f"Ollama raw output: {output[:500]}")
                    parsed = extract_json(output)
                    if parsed:
                        logger.info(f"Parsed intent from Ollama: {parsed}")
                        return parsed
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return {"error": f"Ollama error: {response.status_code}"}
        except Exception as e:
            logger.warning(f"Ollama exception: {e}, using rule-based fallback")

        # Final fallback: rule-based parser
        logger.info("Using rule-based parser")
        return rule_based_parse(message)


async def call_backend(intent: dict, user_token: str):
    """Call backend API based on parsed intent"""
    headers = {"Content-Type": "application/json"}
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        action = intent.get("action", "").upper()
        
        # CREATE TODO
        if action == "CREATE":
            todos = intent.get("todos", [])
            created = []
            
            for todo_data in todos:
                logger.info(f"Creating todo: {todo_data}")
                payload = {
                    "title": todo_data.get("title", "Untitled"),
                    "priority": todo_data.get("priority", "MEDIUM").lower()
                }
                
                try:
                    response = await client.post(
                        f"{BACKEND_API_URL}/api/todos/",
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code >= 400:
                        logger.error(f"Backend error: {response.status_code} - {response.text[:200]}")
                        return {"error": f"Backend error: {response.status_code}"}
                    
                    created.append(response.json())
                except Exception as e:
                    logger.error(f"Create todo exception: {e}")
                    return {"error": str(e)}
            
            return {"created": created, "count": len(created)}
        
        # LIST TODOS
        elif action == "LIST":
            try:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/todos/",
                    headers=headers
                )
                
                if response.status_code >= 400:
                    return {"error": f"Backend error: {response.status_code}"}
                
                return response.json()
            except Exception as e:
                return {"error": str(e)}
        
        # DELETE TODO
        elif action == "DELETE":
            title = intent.get("title", "").lower()
            
            # First, get all todos to find matching ones
            try:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/todos/",
                    headers=headers
                )
                
                if response.status_code >= 400:
                    return {"error": f"Backend error: {response.status_code}"}
                
                todos = response.json()
                
                # Find todos with matching title
                deleted = []
                for todo in todos:
                    if title in todo.get("title", "").lower():
                        del_response = await client.delete(
                            f"{BACKEND_API_URL}/api/todos/{todo['id']}/",
                            headers=headers
                        )
                        
                        if del_response.status_code < 400:
                            deleted.append(todo)
                
                return {"deleted": deleted, "count": len(deleted)}
                
            except Exception as e:
                return {"error": str(e)}
        
        # UPDATE TODO
        elif action == "UPDATE":
            title = intent.get("title", "").lower()
            status = intent.get("status", "completed")
            
            # Get all todos and find matching ones
            try:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/todos/",
                    headers=headers
                )
                
                if response.status_code >= 400:
                    return {"error": f"Backend error: {response.status_code}"}
                
                todos = response.json()
                
                # Update matching todos
                updated = []
                for todo in todos:
                    if title in todo.get("title", "").lower():
                        update_response = await client.put(
                            f"{BACKEND_API_URL}/api/todos/{todo['id']}",
                            json={"status": status},
                            headers=headers
                        )
                        
                        if update_response.status_code < 400:
                            updated.append(update_response.json())
                
                return {"updated": updated, "count": len(updated)}
                
            except Exception as e:
                return {"error": str(e)}
        
        else:
            return {"error": "Unknown action"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Hybrid Todo Chatbot",
        "version": "2.3.0",
        "agent": "Qwen API + Ollama fallback",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "websocket": "/ws/chat/{token}"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""

    qwen_status = "ok" if QWEN_API_KEY else "not_configured"

    # Check Ollama
    ollama_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GordonAgent.OLLAMA_API_URL}/api/tags")
            ollama_status = "ok" if response.status_code == 200 else "error"
    except:
        ollama_status = "not_available"

    return {
        "status": "healthy",
        "service": "hybrid-chatbot",
        "providers": {
            "qwen": {"status": qwen_status, "api_url": GordonAgent.QWEN_API_URL},
            "ollama": {"status": ollama_status, "api_url": GordonAgent.OLLAMA_API_URL}
        },
        "models": {
            "qwen": "qwen-plus",
            "ollama": GordonAgent.OLLAMA_MODEL
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.websocket("/ws/chat/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        # Send greeting
        await websocket.send_json({
            "type": "message",
            "text": "👋 Hello! I'm Gordon, your AI Todo Agent.\n\n"
                   "Try:\n"
                   "• 'task buy milk' - create new todo\n"
                   "• 'urgent task fix bug' - create high priority\n"
                   "• 'show my tasks' - list all todos\n"
                   "• 'delete buy milk' - remove todo\n"
                   "• 'mark done fix bug' - complete todo"
        })
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            user_message = msg_data.get("message", "").strip()
            
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "text": "⚠️ Empty message"
                })
                continue
            
            # Parse with Gordon Agent
            intent = await GordonAgent.parse_message(user_message)
            
            if "error" in intent:
                await websocket.send_json({
                    "type": "error",
                    "text": f"❌ {intent.get('error')}"
                })
                continue
            
            action = intent.get("action", "").upper()
            
            # Execute action via backend
            result = await call_backend(intent, token)
            
            if "error" in result:
                await websocket.send_json({
                    "type": "error",
                    "text": f"❌ Error: {result.get('error')}"
                })
                continue
            
            # Format response based on action
            if action == "CREATE":
                count = result.get("count", 0)
                await websocket.send_json({
                    "type": "success",
                    "text": f"✅ Created {count} todo{'s' if count > 1 else ''}!",
                    "data": result.get("created")
                })
            
            elif action == "LIST":
                todos = result if isinstance(result, list) else []
                
                if not todos:
                    await websocket.send_json({
                        "type": "message",
                        "text": "📭 You have no todos yet!"
                    })
                else:
                    # Format todo list
                    text = f"📋 **Your Todos ({len(todos)}):**\n\n"
                    
                    for todo in todos:
                        priority = todo.get("priority", "medium").upper()
                        status = todo.get("status", "pending")
                        title = todo.get("title", "Untitled")
                        
                        emoji = "🔴" if priority == "HIGH" else "🟡" if priority == "MEDIUM" else "🟢"
                        check = "✅" if status == "completed" else "⏳"
                        
                        text += f"{check} {emoji} {title} [{priority}]\n"
                    
                    await websocket.send_json({
                        "type": "todos",
                        "text": text,
                        "count": len(todos),
                        "data": todos
                    })
            
            elif action == "DELETE":
                count = result.get("count", 0)
                
                if count == 0:
                    await websocket.send_json({
                        "type": "warning",
                        "text": f"⚠️ No todo found matching: '{intent.get('title')}'"
                    })
                else:
                    await websocket.send_json({
                        "type": "success",
                        "text": f"🗑️ Deleted {count} todo{'s' if count > 1 else ''}!",
                        "data": result.get("deleted")
                    })
            
            elif action == "UPDATE":
                count = result.get("count", 0)
                
                if count == 0:
                    await websocket.send_json({
                        "type": "warning",
                        "text": f"⚠️ No todo found matching: '{intent.get('title')}'"
                    })
                else:
                    status_emoji = "✅" if intent.get("status") == "completed" else "⏳"
                    await websocket.send_json({
                        "type": "success",
                        "text": f"{status_emoji} Updated {count} todo{'s' if count > 1 else ''}!",
                        "data": result.get("updated")
                    })
            
            else:
                await websocket.send_json({
                    "type": "message",
                    "text": "🤔 I didn't understand that. Try:\n"
                           "• 'task [description]'\n"
                           "• 'delete [task name]'\n"
                           "• 'show'\n"
                           "• 'mark done [task name]'"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for token: {token}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """REST endpoint for chat (non-WebSocket)"""
    try:
        logger.info(f"REST chat message: {request.message[:100]}...")
        
        # Parse with Gordon
        intent = await GordonAgent.parse_message(request.message)
        
        if "error" in intent:
            return {
                "response": f"❌ {intent.get('error')}",
                "intent": intent
            }
        
        # Execute via backend
        result = await call_backend(intent, request.user_token)
        
        # Format response
        action = intent.get("action", "").upper()
        
        if "error" in result:
            response_text = f"❌ Error: {result.get('error')}"
        elif action == "CREATE":
            count = result.get("count", 0)
            response_text = f"✅ Created {count} todo{'s' if count > 1 else ''}!"
        elif action == "LIST":
            todos = result if isinstance(result, list) else []
            response_text = f"📋 You have {len(todos)} todo{'s' if len(todos) != 1 else ''}"
        elif action == "DELETE":
            count = result.get("count", 0)
            response_text = f"🗑️ Deleted {count} todo{'s' if count > 1 else ''}!" if count > 0 else "⚠️ No matching todo found"
        elif action == "UPDATE":
            count = result.get("count", 0)
            response_text = f"✅ Updated {count} todo{'s' if count > 1 else ''}!" if count > 0 else "⚠️ No matching todo found"
        else:
            response_text = "✅ Done"
        
        return {
            "response": response_text,
            "intent": intent,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Chat exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
