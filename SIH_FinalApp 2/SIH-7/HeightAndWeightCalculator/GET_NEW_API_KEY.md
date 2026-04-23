# How to Get a Valid Gemini API Key

## The Problem
The API key `AIzaSyD3gzb4NbA_YjTEq39GNGudTJHRgWWhPk4` is either:
- Invalid
- Expired
- Doesn't have Gemini API access enabled
- Has exceeded quota

## Solution: Get a New API Key

### Step 1: Go to Google AI Studio
Visit: https://makersuite.google.com/app/apikey

OR

Visit: https://aistudio.google.com/app/apikey

### Step 2: Sign In
- Sign in with your Google account
- Accept terms of service if prompted

### Step 3: Create API Key
1. Click "Create API Key" button
2. Select "Create API key in new project" (or use existing project)
3. Copy the generated API key

### Step 4: Update the API Key

**File: chatbot_routes.py**
```python
GEMINI_API_KEY = "YOUR_NEW_API_KEY_HERE"
```

**File: test_api_quick.py**
```python
API_KEY = "YOUR_NEW_API_KEY_HERE"
```

### Step 5: Test the New Key
```bash
python test_api_quick.py
```

### Step 6: Restart Flask Server
```bash
# Stop server with Ctrl+C
python app.py
```

## Alternative: Use Environment Variable

### Option 1: Set in Windows
```cmd
set GEMINI_API_KEY=your_api_key_here
python app.py
```

### Option 2: Create .env file
Create a file named `.env` in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

Then update chatbot_routes.py:
```python
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

## Verify API Key Works

### Test 1: Quick Test
```bash
python test_api_quick.py
```

Should show:
```
✓ API key configured
Testing: gemini-pro
✓ gemini-pro WORKS!
Response: Hello! How can I help you today?
```

### Test 2: In Browser
1. Open chatbot
2. Type "Hello"
3. Should get response

## Common Issues

### Issue: "API key not valid"
**Solution:** Get a new API key from https://makersuite.google.com/app/apikey

### Issue: "Quota exceeded"
**Solution:** 
- Wait 24 hours for quota reset
- Or create new Google account and get new API key

### Issue: "Permission denied"
**Solution:**
- Ensure Gemini API is enabled in Google Cloud Console
- Check API key has proper permissions

### Issue: "Model not found"
**Solution:**
- Use `gemini-pro` model (most compatible)
- Ensure API key has access to Gemini models

## Free Tier Limits

Gemini API Free Tier:
- 60 requests per minute
- 1,500 requests per day
- Free forever

If you need more:
- Upgrade to paid plan
- Or create multiple API keys with different Google accounts

## Important Notes

1. **Never share your API key publicly**
2. **Don't commit API keys to Git**
3. **Use environment variables in production**
4. **Rotate keys regularly for security**

## Quick Fix for Testing

If you need to test immediately and don't have a valid key:

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Get API Key"
3. Copy the key
4. Replace in chatbot_routes.py
5. Restart server
6. Test chatbot

## Verification Checklist

- [ ] Got new API key from Google AI Studio
- [ ] Updated chatbot_routes.py with new key
- [ ] Updated test_api_quick.py with new key
- [ ] Ran test_api_quick.py successfully
- [ ] Restarted Flask server
- [ ] Tested chatbot in browser
- [ ] Received response without errors

## Support Links

- Get API Key: https://makersuite.google.com/app/apikey
- Gemini API Docs: https://ai.google.dev/docs
- Google Cloud Console: https://console.cloud.google.com/
- API Quotas: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
