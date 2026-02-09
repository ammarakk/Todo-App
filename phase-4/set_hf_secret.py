#!/usr/bin/env python3
"""
Set HuggingFace Space Secrets using requests library
"""
import requests
import sys

SPACE_ID = "ammaraak/todo-backend-new"
TOKEN = "YmvKbo1MdR024LGd9t8CVRLR"  # Original token

# Secrets to set
SECRETS = {
    "GEMINI_API_KEY": "AIzaSyCWV3opImJIT_KhSyti9qdGTnxC_pPnca4",
    "AI_PROVIDER": "gemini",
}

def main():
    print(f"Setting secrets on HuggingFace Space: {SPACE_ID}")
    print()

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    for key, value in SECRETS.items():
        url = f"https://huggingface.co/api/spaces/{SPACE_ID}/secrets/{key}"

        print(f"Setting {key}...")

        # First try to delete if exists
        try:
            delete_response = requests.delete(url, headers=headers, timeout=10)
            if delete_response.status_code == 200:
                print(f"  - Deleted existing {key}")
        except Exception as e:
            pass

        # Add the secret
        try:
            response = requests.post(
                f"https://huggingface.co/api/spaces/{SPACE_ID}/secrets",
                headers=headers,
                json={"key": key, "value": value},
                timeout=30
            )

            if response.status_code == 200:
                print(f"  OK {key} set successfully")
            elif response.status_code == 401:
                print(f"  FAIL: Token is invalid or expired")
                print(f"  Please get a new token from: https://huggingface.co/settings/tokens")
                return
            else:
                print(f"  FAIL: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  FAIL: {e}")

    print()
    print("Done! The space will restart automatically.")

if __name__ == "__main__":
    main()
