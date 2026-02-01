# Test script for Phase III Chat API
# Tests the /api/chat endpoint with sample messages

import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000"

# For testing without JWT, create a test token
# In production, users get this from Phase II /auth/login
TEST_USER_ID = str(uuid4())  # Replace with actual user ID from your database

def get_test_jwt():
    """
    Get a test JWT token.
    For now, this is a placeholder.
    In production, users login via Phase II backend.
    """
    # TODO: Implement actual JWT generation or get from login
    # For testing, you might need to:
    # 1. Create a user in the database
    # 2. Call /auth/login to get JWT
    # 3. Use that JWT here
    return "YOUR_JWT_TOKEN_HERE"

def test_chat_endpoint():
    """Test the chat endpoint with various messages"""

    headers = {
        "Authorization": f"Bearer {get_test_jwt()}",
        "Content-Type": "application/json"
    }

    test_cases = [
        {
            "name": "Create task (English)",
            "message": "Add a task to buy milk"
        },
        {
            "name": "Create task (Urdu)",
            "message": "Doodh lene ka task add karo"
        },
        {
            "name": "Create task with priority",
            "message": "Add task 'Finish project' with high priority"
        },
        {
            "name": "Create task with due date",
            "message": "Add task 'Submit report' due 2026-02-01"
        },
        {
            "name": "List tasks",
            "message": "Show my tasks"
        },
        {
            "name": "List tasks (Urdu)",
            "message": "Mere tasks dikhao"
        }
    ]

    print("=" * 60)
    print("PHASE III CHAT API TEST")
    print("=" * 60)

    for test in test_cases:
        print(f"\n[Test] {test['name']}")
        print(f"Message: {test['message']}")

        payload = {
            "message": test['message']
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/chat/",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"Reply: {data.get('reply', 'No reply')[:100]}...")
                print(f"Conversation ID: {data.get('conversation_id')}")
                if data.get('tool_calls'):
                    print(f"Tool Calls: {len(data['tool_calls'])} tool(s) executed")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Error: {response.text}")

        except Exception as e:
            print(f"❌ Exception: {str(e)}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

def test_health_endpoints():
    """Test health check endpoints"""

    print("\n[Health Check] Testing endpoints...")

    endpoints = [
        ("/", "Root"),
        ("/health", "Main Health"),
        ("/api/chat/health", "Chat Health")
    ]

    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║     Phase III - AI-Powered Todo Chatbot Test Suite         ║
║                                                             ║
║  Before running, ensure:                                   ║
║  1. Backend server is running (port 8000)                  ║
║  2. You have a valid JWT token from Phase II               ║
║  3. Update get_test_jwt() with your token                  ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Test health endpoints
    test_health_endpoints()

    # Test chat endpoint
    print("\n" + "⚠️  NOTE: You need a valid JWT token to test /api/chat")
    print("Update get_test_jwt() function with your token first!")
    print("\nSkipping chat tests... (uncomment after adding JWT)\n")
    # test_chat_endpoint()
