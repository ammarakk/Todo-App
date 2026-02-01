"""
Chatbot Service - Phase IV
FastAPI middleware that connects AI (OpenAI/Ollama) to Backend APIs
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import logging
from typing import Optional
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Todo Chatbot Service", version="1.0.0")

# Environment variables
OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://ollama-service:11434")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend-service:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:3b")

# Qwen API Configuration
USE_QWEN_API = os.getenv("USE_QWEN_API", "true").lower() == "true"
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "0XA2TcDarwQtRtWP-uwkwY2L3PCkWHFuzQkxWyW1r2Xm58q5dR81tBuQSTAvW7AKppM8D0GRseYZb8AZ-cMtiQ")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# Initialize OpenAI-compatible client for Qwen
qwen_client = None
if USE_QWEN_API and QWEN_API_KEY:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL
    )
    logger.info(f"Using Qwen API via {QWEN_BASE_URL}")
else:
    logger.info("Using direct keyword extraction (no AI API)")


class ChatRequest(BaseModel):
    message: str
    user_token: Optional[str] = None


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}


async def ask_ollama(message: str) -> str:
    """Send message to Ollama and get response"""
    async with httpx.AsyncClient(timeout=600.0) as client:  # Increased to 10 minutes for CPU inference
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": message,
                "stream": False,
                "options": {
                    "num_ctx": 256,  # Reduced context window for faster inference
                    "num_predict": 50  # Limit response length
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


async def extract_intent_qwen(message: str) -> dict:
    """
    Extract intent using Qwen API (fast, accurate, supports Chinese/English)
    Fallback to direct extraction if API fails
    """
    try:
        response = qwen_client.chat.completions.create(
            model="qwen-turbo",  # Fast and cost-effective
            messages=[
                {
                    "role": "system",
                    "content": """You are a todo intent extractor. Extract the action and details from user messages.
Return ONLY JSON in this format: {"action": "create/read/update/delete", "title": "...", "id": ..., "params": {...}}

Actions:
- create: when user wants to add/make/create a new todo
- read: when user wants to see/list/get their todos
- update: when user wants to change/modify/mark a todo
- delete: when user wants to remove/delete a todo

Examples:
"add a todo to buy milk" -> {"action": "create", "title": "buy milk"}
"show my todos" -> {"action": "read"}
"mark todo 1 as complete" -> {"action": "update", "id": 1, "params": {"status": "completed"}}
"delete todo 2" -> {"action": "delete", "id": 2}

Return ONLY valid JSON, no explanations."""
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.3,
            max_tokens=100
        )

        content = response.choices[0].message.content.strip()
        logger.info(f"Qwen response: {content}")

        # Parse JSON response
        import json
        intent = json.loads(content)

        # Validate required fields
        if "action" not in intent:
            raise ValueError("No action in response")

        return intent

    except Exception as e:
        logger.error(f"Qwen API extraction failed: {e}, falling back to direct extraction")
        return extract_intent_direct(message)


def extract_intent_direct(message: str) -> dict:
    """
    Direct keyword-based intent extraction (no LLM needed)
    Fast and works on CPU-only systems
    """
    msg_lower = message.lower().strip()

    # Create/Add/Insert keywords
    if any(word in msg_lower for word in ["add", "create", "new", "insert", "make", "todo"]):
        # Extract title from message
        title = message
        # Remove common prefixes
        for prefix in ["add a todo", "add todo", "create a todo", "create todo",
                       "make a todo", "make todo", "insert", "new todo"]:
            if prefix in msg_lower:
                title = message.lower().replace(prefix, "").strip()
                break

        return {"action": "create", "title": title.title() if title else "Untitled"}

    # Read/Show/List/Get keywords
    elif any(word in msg_lower for word in ["show", "list", "get", "read", "my todos", "all todos"]):
        return {"action": "read"}

    # Update/Edit/Modify keywords
    elif any(word in msg_lower for word in ["update", "edit", "modify", "change", "mark"]):
        # Look for todo ID
        words = msg_lower.split()
        todo_id = None
        for i, word in enumerate(words):
            if word.isdigit():
                todo_id = int(word)
                break

        # Check if marking as complete
        if "complete" in msg_lower or "done" in msg_lower:
            return {"action": "update", "id": todo_id, "params": {"status": "completed"}}

        return {"action": "update", "id": todo_id, "params": {}}

    # Delete/Remove keywords
    elif any(word in msg_lower for word in ["delete", "remove", "erase"]):
        words = msg_lower.split()
        for word in words:
            if word.isdigit():
                return {"action": "delete", "id": int(word)}

        return {"action": "read"}  # Fallback

    else:
        return {"action": "read"}  # Default to showing todos


def parse_intent(llm_response: str) -> dict:
    """
    Extract intent from LLM response
    Returns: {action: str, params: dict}
    """
    response_lower = llm_response.lower()
    
    # Simple keyword-based intent extraction (FS-IMP-4)
    if any(word in response_lower for word in ["add", "create", "insert", "new"]):
        # Extract title from response
        title = llm_response.split("create")[-1].split("todo")[0].strip()
        return {"action": "create", "title": title}
    
    elif any(word in response_lower for word in ["delete", "remove", "erase"]):
        # Extract ID from response
        words = response_lower.split()
        for word in words:
            if word.isdigit():
                return {"action": "delete", "id": int(word)}
        return {"action": "read"}  # Fallback
    
    elif any(word in response_lower for word in ["update", "edit", "modify", "change"]):
        words = response_lower.split()
        for word in words:
            if word.isdigit():
                return {"action": "update", "id": int(word)}
        return {"action": "read"}
    
    else:
        return {"action": "read"}


async def call_backend(intent: dict, user_token: str):
    """Call backend API based on intent"""
    headers = {"Content-Type": "application/json"}
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"

    async with httpx.AsyncClient(timeout=60.0) as client:  # Increased backend timeout
        if intent["action"] == "create":
            logger.info(f"Calling backend CREATE at {BACKEND_API_URL}/api/todos/")
            response = await client.post(
                f"{BACKEND_API_URL}/api/todos/",
                json={"title": intent.get("title", "Untitled")},
                headers=headers
            )
            logger.info(f"Backend response status: {response.status_code}")
            logger.info(f"Backend response text: {response.text[:500]}")
            if response.status_code >= 400:
                return {"error": f"Backend error: {response.status_code}", "detail": response.text[:200]}
            try:
                return response.json()
            except Exception as e:
                logger.error(f"JSON parse error: {e}, response text: {response.text[:500]}")
                return {"error": "JSON parse error", "raw_response": response.text[:500], "exception": str(e)}

        elif intent["action"] == "read":
            response = await client.get(
                f"{BACKEND_API_URL}/api/todos/",
                headers=headers
            )
            if response.status_code >= 400:
                return {"error": f"Backend error: {response.status_code}", "detail": response.text[:200]}
            try:
                return response.json()
            except Exception as e:
                return {"error": "JSON parse error", "raw_response": response.text[:500], "exception": str(e)}

        elif intent["action"] == "update":
            todo_id = intent.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="Todo ID required")
            response = await client.put(
                f"{BACKEND_API_URL}/api/todos/{todo_id}/",
                json=intent.get("params", {}),
                headers=headers
            )
            if response.status_code >= 400:
                return {"error": f"Backend error: {response.status_code}", "detail": response.text[:200]}
            try:
                return response.json()
            except Exception as e:
                return {"error": "JSON parse error", "raw_response": response.text[:500], "exception": str(e)}

        elif intent["action"] == "delete":
            todo_id = intent.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="Todo ID required")
            response = await client.delete(
                f"{BACKEND_API_URL}/api/todos/{todo_id}/",
                headers=headers
            )
            if response.status_code >= 400:
                return {"error": f"Backend error: {response.status_code}", "detail": response.text[:200]}
            try:
                return response.json()
            except Exception as e:
                return {"error": "JSON parse error", "raw_response": response.text[:500], "exception": str(e)}

        else:
            # FS-IMP-7: Block unsupported features
            return {"message": "Not supported in Phase IV"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint (FS-IMP-6)
    Flow: User message → Qwen API → Intent extraction → Backend API → Response
    """
    try:
        logger.info(f"Received chat message: {request.message[:100]}...")

        # Step 1: Intent extraction - Try Qwen API first, fallback to direct
        if qwen_client:
            logger.info("Using Qwen API for intent extraction")
            intent = await extract_intent_qwen(request.message)
        else:
            logger.info("Using direct keyword extraction")
            intent = extract_intent_direct(request.message)
        logger.info(f"Extracted intent: {intent}")

        # Step 2: Call backend API
        logger.info(f"Calling backend at {BACKEND_API_URL}")
        result = await call_backend(intent, request.user_token)
        logger.info(f"Backend result: {result}")

        # Generate response message
        if result and "error" not in result:
            if intent["action"] == "create":
                response_msg = f"✅ Todo created: {result.get('title', 'Untitled')}"
            elif intent["action"] == "read":
                count = len(result) if isinstance(result, list) else 0
                response_msg = f"📋 You have {count} todo(s)"
            elif intent["action"] == "update":
                response_msg = "✅ Todo updated"
            elif intent["action"] == "delete":
                response_msg = "🗑️ Todo deleted"
            else:
                response_msg = "✅ Done"
        else:
            response_msg = f"❌ Error: {result.get('error', 'Unknown error') if result else 'Failed'}"

        return {
            "response": response_msg,
            "intent": intent,
            "result": result
        }

    except httpx.HTTPError as e:
        logger.error(f"HTTPError: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {type(e).__name__} - {str(e)}"
        )
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {type(e).__name__} - {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
