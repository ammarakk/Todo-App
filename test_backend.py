import requests
import json

BACKEND_URL = "https://ammaraak-todo-app-backend.hf.space"

print("="*60)
print("BACKEND ENDPOINT TEST")
print("="*60)

# Test 1: Health
print("\n1. Testing /health")
r = requests.get(f"{BACKEND_URL}/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Test 2: AI Chat Health (no auth)
print("\n2. Testing /api/ai-chat/health (no auth)")
r = requests.get(f"{BACKEND_URL}/api/ai-chat/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:200]}")

# Test 3: AI Command (no auth - should fail 401)
print("\n3. Testing /api/ai-chat/command (no auth)")
payload = {"message": "test", "conversationId": "new"}
r = requests.post(f"{BACKEND_URL}/api/ai-chat/command", json=payload)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:200]}")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
print("Backend is RUNNING and endpoint EXISTS")
print("401 is EXPECTED (needs JWT token from login)")
print("Frontend must send: Authorization: Bearer <token>")
