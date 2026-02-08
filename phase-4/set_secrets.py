#!/usr/bin/env python3
"""
Set HuggingFace Space Secrets via HuggingFace Hub API
"""
import sys
from huggingface_hub import HfApi

# Space repository
SPACE_REPO = "ammaraak/todo-backend-new"
TOKEN = "YmvKbo1MdR024LGd9t8CVRLR"  # Write token

# Secrets to set
SECRETS = {
    "AI_PROVIDER": "gemini",
    "GEMINI_API_KEY": "AIzaSyCWV3opImJIT_KhSyti9qdGTnxC_pPnca4",
}

def main():
    print(f"Setting secrets on HuggingFace Space: {SPACE_REPO}")
    print()

    api = HfApi(token=TOKEN)

    for key, value in SECRETS.items():
        try:
            # Check if secret already exists and has correct value
            try:
                existing = api.get_space_secret(key, repo_id=SPACE_REPO)
                if existing.value == value:
                    print(f"OK {key}: already set correctly")
                    continue
                else:
                    print(f"~ {key}: updating...")
            except Exception:
                print(f"+ {key}: setting...")

            # Set or update the secret
            api.add_space_secret(
                repo_id=SPACE_REPO,
                key=key,
                value=value
            )
            print(f"  OK {key} set successfully")
        except Exception as e:
            print(f"  FAIL: Failed to set {key}: {e}")

    print()
    print("Done! The space will restart automatically.")
    print("AI Configuration:")
    print(f"  AI_PROVIDER: {SECRETS['AI_PROVIDER']}")
    print(f"  GEMINI_API_KEY: ***set***")

if __name__ == "__main__":
    main()
