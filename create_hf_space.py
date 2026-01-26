from huggingface_hub import HfApi
import sys

try:
    # Replace with your actual token
    api = HfApi(token="YOUR_HF_TOKEN_HERE")
    api.create_repo(
        repo_id="ammaraak/todo-app-backend",
        repo_type="space",
        space_sdk="docker"
    )
    print("Space created successfully!")
    print("URL: https://huggingface.co/spaces/ammaraak/todo-app-backend")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
