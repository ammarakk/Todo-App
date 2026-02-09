import os
import sys

# Set token as environment variable
os.environ['HF_TOKEN'] = 'YmvKbo1MdR024LGd9t8CVRLR'
os.environ['HUGGINGFACE_HUB_TOKEN'] = 'YmvKbo1MdR024LGd9t8CVRLR'

try:
    from huggingface_hub import HfApi

    api = HfApi()

    # Test authentication
    try:
        whoami = api.whoami()
        print(f"Authenticated as: {whoami}")
    except Exception as e:
        print(f"Auth failed: {e}")
        print("\nThe token is invalid or expired.")
        print("Please get a new token from: https://huggingface.co/settings/tokens")
        print("\nThen update the script with the new token.")
        sys.exit(1)

    # Set the secret
    SPACE_ID = "ammaraak/todo-backend-new"

    try:
        api.add_space_secret(
            repo_id=SPACE_ID,
            key="GEMINI_API_KEY",
            value="AIzaSyCWV3opImJIT_KhSyti9qdGTnxC_pPnca4"
        )
        print("OK: GEMINI_API_KEY secret set successfully")

        api.add_space_secret(
            repo_id=SPACE_ID,
            key="AI_PROVIDER",
            value="gemini"
        )
        print("OK: AI_PROVIDER secret set successfully")

        print("\nDone! The space will restart automatically.")

    except Exception as e:
        print(f"Failed to set secrets: {e}")

except ImportError as e:
    print(f"Import error: {e}")
    print("Please install: pip install huggingface-hub")
