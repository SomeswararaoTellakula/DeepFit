# Gemini Chatbot Troubleshooting Guide

## Quick Fix Steps

### 1. Test API Connection First
```bash
python test_gemini_api.py
```

This will:
- Verify your API key works
- List all available models
- Test text generation
- Show recommended models to use

### 2. Common Errors and Solutions

#### Error: "404 models/gemini-1.5-flash is not found"

**Solution**: The chatbot now automatically detects available models. Just restart your Flask app:
```bash
python app.py
```

The chatbot will print which models it's using:
```
Using text model: gemini-pro
Using vision model: gemini-pro-vision
```

#### Error: "API quota exceeded"

**Solutions**:
1. Check your API quota at: https://makersuite.google.com/app/apikey
2. Wait for quota reset (usually daily)
3. Upgrade your API plan if needed

#### Error: "Unable to connect to chatbot service"

**Solutions**:
1. Check internet connection
2. Verify Flask app is running
3. Check browser console for errors (F12)
4. Ensure chatbot routes are registered in app.py

#### Error: "Voice recognition not working"

**Solutions**:
1. Use Chrome or Edge browser (best support)
2. Allow microphone permissions
3. Use HTTPS (required for microphone access)
4. Check browser console for errors

#### Error: "Camera not working"

**Solutions**:
1. Allow camera permissions in browser
2. Close other apps using camera
3. Use HTTPS (required for camera access)
4. Try a different browser

### 3. Verify Installation

Check if all dependencies are installed:
```bash
pip list | findstr google-generativeai
pip list | findstr Pillow
```

Should show:
```
google-generativeai    x.x.x
Pillow                 x.x.x
```

### 4. Check Flask Routes

Verify chatbot routes are registered:
```python
# In app.py, should have:
from chatbot_routes import chatbot_bp
app.register_blueprint(chatbot_bp)
```

### 5. Test Individual Components

#### Test Text Chat:
```bash
curl -X POST http://localhost:5000/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello\"}"
```

#### Test in Browser Console:
```javascript
fetch('/api/chatbot/message', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'Hello'})
})
.then(r => r.json())
.then(d => console.log(d));
```

### 6. Enable Debug Mode

Add to your Flask app:
```python
app.config['DEBUG'] = True
```

This will show detailed error messages.

### 7. Check Browser Console

1. Open browser (F12)
2. Go to Console tab
3. Look for red error messages
4. Check Network tab for failed requests

### 8. Common Browser Issues

#### Chatbot widget not appearing:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check if chatbot_widget.html is included in base.html
4. Verify JavaScript is enabled

#### Styling issues:
1. Check if CSS is loading (Network tab)
2. Clear browser cache
3. Check for CSS conflicts

### 9. API Key Issues

#### Verify API key is valid:
1. Go to: https://makersuite.google.com/app/apikey
2. Check if key is active
3. Verify API is enabled for your project
4. Check usage limits

#### Update API key:
In `chatbot_routes.py`:
```python
GEMINI_API_KEY = "YOUR_NEW_API_KEY_HERE"
```

### 10. Model Compatibility

The chatbot now supports multiple models:
- gemini-1.5-pro (best quality)
- gemini-1.5-flash (fastest)
- gemini-pro (stable)
- gemini-pro-vision (images)

It automatically selects the best available model.

### 11. File Upload Issues

#### File too large:
- Maximum file size: 5MB
- Compress images before uploading
- Split large text files

#### Unsupported file type:
Supported formats:
- Images: PNG, JPG, JPEG, GIF, BMP, WEBP
- Text: TXT, CSV, JSON, MD, etc.

### 12. Performance Issues

#### Slow responses:
1. Check internet speed
2. Use gemini-1.5-flash for faster responses
3. Reduce image sizes before upload
4. Clear chat history periodically

#### Memory issues:
1. Reset chat history (click reset button)
2. Restart Flask app
3. Clear browser cache

### 13. Production Deployment

For production, add:

1. **Environment Variables**:
```python
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

2. **Rate Limiting**:
```python
from flask_limiter import Limiter
limiter = Limiter(app)

@chatbot_bp.route('/api/chatbot/message')
@limiter.limit("10 per minute")
def send_message():
    # ...
```

3. **Error Logging**:
```python
import logging
logging.basicConfig(filename='chatbot.log', level=logging.ERROR)
```

### 14. Getting Help

If issues persist:

1. Check Flask logs for errors
2. Run test_gemini_api.py to verify setup
3. Check browser console for JavaScript errors
4. Verify all files are in correct locations
5. Ensure all dependencies are installed

### 15. Reset Everything

If all else fails:

```bash
# 1. Reinstall dependencies
pip uninstall google-generativeai Pillow -y
pip install google-generativeai Pillow

# 2. Clear Python cache
del /s /q __pycache__
del /s /q *.pyc

# 3. Restart Flask
python app.py

# 4. Clear browser cache and hard refresh
```

## Contact Support

For additional help:
- Check CHATBOT_README.md for detailed documentation
- Review error messages in Flask console
- Test API connection with test_gemini_api.py
