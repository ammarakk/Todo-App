#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy backend files to HuggingFace Space and set secrets
"""
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    print("Error: HF_TOKEN environment variable not set")
    print("Usage: HF_TOKEN=your_token python deploy_to_hf.py")
    sys.exit(1)

SPACE_ID = "ammaraak/todo-backend-new"
HF_SPACE_DIR = Path("hf-space")

print(f"Deploying to HuggingFace Space: {SPACE_ID}")
print("=" * 60)

try:
    api = HfApi(token=HF_TOKEN)

    # Upload all files from hf-space directory
    print("\n[1] Uploading files to HuggingFace Space...")

    # Check if directory exists
    if not HF_SPACE_DIR.exists():
        print(f"   [ERROR] Directory {HF_SPACE_DIR} does not exist!")
        sys.exit(1)

    # Upload all files recursively
    file_count = 0
    for file_path in HF_SPACE_DIR.rglob("*"):
        if file_path.is_file():
            # Calculate relative path
            rel_path = file_path.relative_to(HF_SPACE_DIR)

            # Upload file
            try:
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=str(rel_path),
                    repo_id=SPACE_ID,
                    repo_type="space",
                    token=HF_TOKEN
                )
                file_count += 1
                print(f"   [OK] Uploaded: {rel_path}")
            except Exception as e:
                print(f"   [ERROR] Failed to upload {rel_path}: {e}")

    print(f"\n   [OK] Total {file_count} files uploaded")

    # Set secrets
    print("\n[2] Setting secrets in HuggingFace Space...")
    print("   Reading secrets from environment variables...")

    secrets = {}

    # Read secrets from environment
    if db_url := os.environ.get("DATABASE_URL"):
        secrets["DATABASE_URL"] = db_url
    if jwt_secret := os.environ.get("JWT_SECRET"):
        secrets["JWT_SECRET"] = jwt_secret
    if dashscope_key := os.environ.get("DASHSCOPE_API_KEY"):
        secrets["DASHSCOPE_API_KEY"] = dashscope_key
    if qwen_key := os.environ.get("QWEN_API_KEY"):
        secrets["QWEN_API_KEY"] = qwen_key
    if use_qwen := os.environ.get("USE_QWEN_API"):
        secrets["USE_QWEN_API"] = use_qwen
    if frontend_url := os.environ.get("FRONTEND_URL"):
        secrets["FRONTEND_URL"] = frontend_url
    if environment := os.environ.get("ENVIRONMENT"):
        secrets["ENVIRONMENT"] = environment
    if hf_api_key := os.environ.get("HUGGINGFACE_API_KEY"):
        secrets["HUGGINGFACE_API_KEY"] = hf_api_key
    if hf_model := os.environ.get("HF_MODEL"):
        secrets["HF_MODEL"] = hf_model

    if not secrets:
        print("   [WARN] No secrets found in environment variables")
        print("   You can set secrets via:")
        print("   DATABASE_URL=... JWT_SECRET=... python deploy_to_hf.py")
    else:
        print(f"   Found {len(secrets)} secrets to set")

    for key, value in secrets.items():
        try:
            # First, try to update secret (it will add if doesn't exist)
            api.add_space_secret(
                repo_id=SPACE_ID,
                key=key,
                value=value,
                token=HF_TOKEN
            )
            print(f"   [OK] Set secret: {key}")
        except Exception as e:
            # If it already exists, we need to update it
            # For now, just note it
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"   [SKIP] Secret already exists: {key}")
            else:
                print(f"   [WARN] Could not set {key}: {e}")

    print("\n" + "=" * 60)
    print("[OK] Deployment completed!")
    print(f"[URL] https://huggingface.co/spaces/{SPACE_ID}")
    print("\n[NEXT] Steps:")
    print("   1. Wait for the Space to build (check the 'Logs' tab)")
    print("   2. Once built, the API will be available at:")
    print(f"      https://ammaraak-todo-backend-new.hf.space")
    print("   3. Update frontend to use this new backend URL")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
