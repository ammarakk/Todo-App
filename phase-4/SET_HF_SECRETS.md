# How to Set HuggingFace Space Secrets Manually

## Problem
The AI chat returns "API error occurred: 404" because the GEMINI_API_KEY secret is not configured on the HuggingFace Space.

## Solution (Follow these steps)

### Step 1: Go to your HuggingFace Space
Visit: https://huggingface.co/spaces/ammaraak/todo-backend-new/settings

### Step 2: Navigate to Secrets
1. Click on the **"Settings"** tab
2. Scroll down to **"Repository secrets"** section

### Step 3: Add the Secret
Click **"New secret"** and add:

**Secret Name:** `GEMINI_API_KEY`
**Secret Value:** `AIzaSyCWV3opImJIT_KhSyti9qdGTnxC_pPnca4`

Click **"Create secret"**

### Step 4: Verify AI_PROVIDER is set (optional)
The code already has `ai_provider = 'gemini'` as default, but you can also add this secret if needed:

**Secret Name:** `AI_PROVIDER`
**Secret Value:** `gemini`

### Step 5: Wait for rebuild
The space will automatically restart after secrets are updated. Wait 2-3 minutes.

---

## Verify it's working
After the rebuild, test the AI chat with:
- "Create a task to buy groceries"
- "Show me my tasks"

The AI should respond properly!
