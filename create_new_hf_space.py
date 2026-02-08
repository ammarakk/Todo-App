#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create new HuggingFace Space for Todo Backend
"""
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, login
import shutil

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    print("Error: HF_TOKEN environment variable not set")
    print("Usage: HF_TOKEN=your_token python create_new_hf_space.py")
    sys.exit(1)

SPACE_NAME = "todo-backend-new"  # You can change this
USERNAME = "ammaraak"  # Change to your HF username
SPACE_ID = f"{USERNAME}/{SPACE_NAME}"

print(f"Creating HuggingFace Space: {SPACE_ID}")
print("=" * 60)

try:
    # Login to HuggingFace
    print("\n[1] Logging in to HuggingFace...")
    login(token=HF_TOKEN)
    api = HfApi(token=HF_TOKEN)
    print("   [OK] Logged in successfully")

    # Create new space
    print(f"\n[2] Creating new space: {SPACE_ID}")
    try:
        api.create_repo(
            repo_id=SPACE_ID,
            repo_type="space",
            space_sdk="docker",
            private=False
        )
        print(f"   [OK] Space created successfully!")
        print(f"   [URL] https://huggingface.co/spaces/{SPACE_ID}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"   [WARN] Space already exists, will update files")
        else:
            raise

    # Prepare backend files
    print("\n[3] Preparing backend files for deployment...")
    backend_src = Path("phase-4/apps/todo-backend")
    hf_space_dir = Path("hf-space")

    # Create hf-space directory
    hf_space_dir.mkdir(exist_ok=True)

    # Files to copy
    files_to_copy = [
        "src/main.py",
        "src/api",
        "src/core",
        "src/models",
        "src/schemas",
        "src/services",
        "src/repositories",
        "src/middleware",
        "src/ai",
        "src/mcp",
        "src/utils",
        "requirements.txt",
        "Dockerfile",
        "README.md"
    ]

    for file_path in files_to_copy:
        src = backend_src / file_path
        dst = hf_space_dir / Path(file_path).name

        if src.is_file():
            shutil.copy2(src, dst)
            print(f"   [OK] Copied: {file_path}")
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"   [OK] Copied: {file_path}/")

    # Create README.md for HF Space
    readme_content = """---
title: Todo Backend API
emoji: toolbox
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# Todo Backend API - Phase 4

## FastAPI Backend Service with Qwen AI Integration

### Features
- JWT Authentication
- Todo CRUD operations
- Qwen AI chatbot integration
- PostgreSQL database
- MCP (Model Context Protocol) tools
- Email notifications
- Reminder system

### API Endpoints

**Health Check:**
```bash
GET /health
```

**Authentication:**
```bash
POST /api/auth/register
POST /api/auth/login
POST /api/auth/verify-token
```

**Todos:**
```bash
GET    /api/todos
POST   /api/todos
GET    /api/todos/{id}
PUT    /api/todos/{id}
DELETE /api/todos/{id}
```

**Chat:**
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "add a todo to buy milk",
  "user_token": "your-jwt-token"
}
```

### Environment Variables (Required Secrets)
- `DATABASE_URL` - PostgreSQL connection string (Neon Tech)
- `JWT_SECRET` - JWT signing secret (min 32 chars)
- `DASHSCOPE_API_KEY` - Qwen AI API key from Alibaba Cloud DashScope
- `FRONTEND_URL` - Frontend URL for CORS (default: http://localhost:3000)
- `ENVIRONMENT` - Environment mode (development/production)

### Tech Stack
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Alembic (Database migrations)
- Qwen API (AI integration)
- PostgreSQL (Database)
- Docker (Containerization)

### Author
Ammar Ak - Phase 4 Infrastructure Project
"""
    (hf_space_dir / "README.md").write_text(readme_content)
    print(f"   [OK] Created README.md")

    # Create Procfile for HuggingFace
    procfile_content = """web: uvicorn src.main:app --host 0.0.0.0 --port 7860
"""
    (hf_space_dir / "Procfile").write_text(procfile_content)
    print(f"   [OK] Created Procfile")

    # Update main.py port for HuggingFace
    main_py = hf_space_dir / "main.py"
    if main_py.exists():
        content = main_py.read_text()
        # Ensure it uses port 7860
        if "port=7860" not in content:
            content = content.replace('port=8000', 'port=7860')
        main_py.write_text(content)
        print(f"   [OK] Updated main.py for HF port 7860")

    print(f"\n[4] Setting up secrets for HuggingFace Space...")
    print("   Please manually set these secrets in your HF Space:")
    print(f"   https://huggingface.co/spaces/{SPACE_ID}/settings")
    print("\n   Required secrets:")
    print("   - DATABASE_URL")
    print("   - JWT_SECRET")
    print("   - DASHSCOPE_API_KEY")
    print("   - FRONTEND_URL")
    print("   - ENVIRONMENT")

    print("\n" + "=" * 60)
    print("[OK] Backend files prepared in hf-space/ directory")
    print(f"[NEXT] Steps:")
    print(f"   1. Upload files to: https://huggingface.co/spaces/{SPACE_ID}")
    print(f"   2. Set secrets in Space Settings")
    print(f"   3. Wait for build to complete")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
