# Gordon Todo Chatbot - Setup Instructions

## 🚀 Quick Start

### 1. Set API Key
```bash
# Edit .env file
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Get your key from: https://console.anthropic.com/account/keys

### 2. Build & Run
```bash
# Build Docker image
docker build -t todo-chatbot-gordon .

# Run container
docker run -d \
  --name todo-chatbot \
  --env-file .env \
  -p 8001:8001 \
  todo-chatbot-gordon
```

### 3. Test
```bash
# Health check
curl http://localhost:8001/api/health

# WebSocket test (browser console)
ws = new WebSocket("ws://localhost:8001/ws/chat/user123")
ws.send(JSON.stringify({message: "task buy milk"}))
ws.onmessage = e => console.log(JSON.parse(e.data))
```

## 📋 Features

✅ **Gordon Agent (cagent)** - Docker's AI agent for NLP
✅ **Natural Language** - "urgent task fix bug" → HIGH priority todo
✅ **WebSocket Support** - Real-time chat
✅ **Priority Detection** - Auto-detect from keywords
✅ **CRUD Operations** - Create, Read, Update, Delete

## 🔧 Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx     # Required
BACKEND_API_URL=http://backend:8000  # Optional (default: localhost:8000)
```

## 💬 Usage Examples

```
"task buy milk"              → Create LOW priority
"urgent task fix the bug"    → Create HIGH priority
"show my tasks"              → List all todos
"delete buy milk"            → Delete matching todo
"mark done fix the bug"      → Mark as completed
```

## 🐳 Docker Compose

```yaml
services:
  chatbot:
    build: .
    env_file: .env
    ports:
      - "8001:8001"
    depends_on:
      - backend
```

## 📊 API Endpoints

- `GET /` - Service info
- `GET /api/health` - Health check
- `POST /api/chat` - REST chat endpoint
- `WS /ws/chat/{token}` - WebSocket chat

## 🔍 Debugging

```bash
# View logs
docker logs todo-chatbot

# Check cagent version
docker exec todo-chatbot cagent --version

# Interactive shell
docker exec -it todo-chatbot bash
```

## ⚙️ Configuration

`cagent-config.yaml` contains the Gordon Agent instructions.
Modify to change behavior or add features.

## 🆘 Troubleshooting

**Error: cagent not found**
→ Rebuild image: `docker build --no-cache -t todo-chatbot-gordon .`

**Error: ANTHROPIC_API_KEY not set**
→ Edit `.env` file with your actual key

**Agent timeout**
→ Increase timeout in `src/main.py` (line ~70)
