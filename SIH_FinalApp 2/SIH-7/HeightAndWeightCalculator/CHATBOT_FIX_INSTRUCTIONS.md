# Chatbot Fix Instructions

## Current Status
API Key has been updated to: `AIzaSyD3gzb4NbA_YjTEq39GNGudTJHRgWWhPk4`

## Files Updated
1. ✅ `chatbot_routes.py` - API key updated
2. ✅ `gemini_chatbot.py` - Model selection improved with fallback
3. ✅ `test_gemini_api.py` - API key updated
4. ✅ `test_api_quick.py` - New quick test script

## Steps to Fix

### Step 1: Test API Key
Run this command to test if the API key works:
```bash
python test_api_quick.py
```

This will:
- Test the API key
- Try different Gemini models
- Show which model works
- Display any errors

### Step 2: Restart Flask Server
**IMPORTANT:** You must restart the Flask server for changes to take effect!

1. Stop the current Flask server (Ctrl+C)
2. Start it again:
```bash
python app.py
```

### Step 3: Clear Browser Cache
1. Open browser DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"
4. Or use Ctrl+Shift+Delete to clear cache

### Step 4: Test Chatbot
1. Open the chatbot widget
2. Type: "Hello"
3. Should get response without errors

## Common Issues & Solutions

### Issue 1: "Invalid API key"
**Cause:** API key is wrong or not enabled
**Solution:** 
1. Go to https://makersuite.google.com/app/apikey
2. Verify API key is correct
3. Ensure Gemini API is enabled

### Issue 2: "Model not found"
**Cause:** Model not available with your API key
**Solution:** 
- The code now tries multiple models automatically
- Check test_api_quick.py output to see which model works

### Issue 3: "Quota exceeded"
**Cause:** API usage limit reached
**Solution:**
- Wait for quota reset (usually daily)
- Or upgrade your API plan

### Issue 4: Still showing old error
**Cause:** Server not restarted or browser cache
**Solution:**
1. **Restart Flask server** (most important!)
2. Clear browser cache
3. Hard refresh page (Ctrl+Shift+R)

## Verification Checklist

- [ ] API key updated in chatbot_routes.py
- [ ] API key updated in gemini_chatbot.py  
- [ ] Ran test_api_quick.py successfully
- [ ] Restarted Flask server
- [ ] Cleared browser cache
- [ ] Tested chatbot with "Hello" message
- [ ] Received response without errors

## Model Priority

The chatbot will try these models in order:
1. gemini-1.5-flash (fastest, recommended)
2. gemini-1.5-pro (more capable)
3. gemini-pro (older, stable)
4. gemini-1.0-pro (fallback)

It will use the first one that works.

## Debug Output

When you start the Flask server, you should see:
```
Configuring with API key: AIzaSyD3gz...
Trying model: gemini-1.5-flash
✓ Successfully using model: gemini-1.5-flash
```

If you see errors, check the console output for details.

## Contact Support

If still not working after following all steps:
1. Run test_api_quick.py and save output
2. Check Flask server console for errors
3. Check browser console (F12) for errors
4. Verify API key at https://makersuite.google.com/app/apikey

## Quick Commands

Test API:
```bash
python test_api_quick.py
```

Restart server:
```bash
# Stop with Ctrl+C, then:
python app.py
```

Check if server is running:
```bash
# Should see Flask server output
```
