from huggingface_hub import HfApi

# Replace with your actual token
api = HfApi(token="YOUR_HF_TOKEN_HERE")

# Set JWT_SECRET
api.add_space_secret(
    repo_id="ammaraak/todo-app-backend",
    key="JWT_SECRET",
    value="YOUR_JWT_SECRET_HERE"
)
print("JWT_SECRET added!")

# Set NEON_DATABASE_URL
api.add_space_secret(
    repo_id="ammaraak/todo-app-backend",
    key="NEON_DATABASE_URL",
    value="YOUR_DATABASE_URL_HERE"
)
print("NEON_DATABASE_URL added!")

print("\nAll secrets configured! Your backend will restart automatically.")
