#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from huggingface_hub import HfApi
from pathlib import Path

HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    print("Error: HF_TOKEN environment variable not set")
    print("Usage: HF_TOKEN=your_token python upload_readme.py")
    sys.exit(1)

SPACE_ID = "ammaraak/todo-backend-new"

print("Uploading fixed README.md...")
api = HfApi(token=HF_TOKEN)

readme_path = Path("hf-space/README.md")
api.upload_file(
    path_or_fileobj=str(readme_path),
    path_in_repo="README.md",
    repo_id=SPACE_ID,
    repo_type="space",
    token=HF_TOKEN
)

print("[OK] README.md uploaded successfully!")
print(f"[URL] https://huggingface.co/spaces/{SPACE_ID}")
