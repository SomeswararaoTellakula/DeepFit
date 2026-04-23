# Gemini AI Chatbot Integration

## Overview

A fully integrated AI chatbot powered by Google's Gemini API with voice assistance, camera access, and file upload capabilities. The chatbot appears as a floating widget at the bottom-right corner of every page.

## Features

### 1. **Text Chat**
- Natural conversation with Gemini AI
- Context-aware responses
- Conversation history maintained per session

### 2. **Voice Assistance**
- **Voice Input**: Click the microphone icon to speak your question
- **Voice Output**: Chatbot responses are automatically spoken using text-to-speech
- Supports continuous voice interaction

### 3. **Camera Access**
- Click the camera icon to capture images
- AI analyzes the captured image
- Useful for form checking, exercise analysis, or general image queries

### 4. **File Upload**
- Upload any file type (images, documents, text files, etc.)
- AI analyzes and provides insights about the file content
- Supports image analysis and text extraction

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_chatbot.txt
```

Or install manually:

```bash
pip install google-generativeai Pillow
```

### 2. API Key Configuration

The Gemini API key is already configured in the code:
```python
GEMINI_API_KEY = "AIzaSyAGL0sAosMtJGTjITEPH_j9d9aNzJSebDo"
```

**Note**: For production, move this to environment variables:
```python
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

### 3. Verify Installation

The chatbot is automatically integrated into all pages through `base.html`. No additional setup required.

## Usage

### Accessing the Chatbot

1. **Open the Widget**: Click the purple chat icon at the bottom-right corner of any page
2. **Close the Widget**: Click the X button in the header

### Text Interaction

1. Type your message in the input field
2. Press Enter or click the send button
3. Wait for the AI response (typing indicator will show)
4. Response will be displayed and spoken aloud

### Voice Interaction

1. Click the microphone icon (turns red when recording)
2. Speak your question clearly
3. The text will appear in the input field
4. Click send or press Enter to submit

### Camera Capture

1. Click the camera icon
2. Allow camera permissions when prompted
3. The chatbot will automatically capture and analyze the image
4. AI response will describe what it sees

### File Upload

1. Click the file/attachment icon
2. Select any file from your device
3. The chatbot will analyze the file content
4. Supports:
   - Images (PNG, JPG, GIF, etc.)
   - Text files (TXT, CSV, JSON, etc.)
   - Documents (with text extraction)

## File Structure

```
HeightAndWeightCalculator/
├── gemini_chatbot.py           # Core chatbot logic
├── chatbot_routes.py           # Flask API endpoints
├── templates/
│   ├── base.html              # Updated with chatbot widget
│   └── chatbot_widget.html    # Chatbot UI component
├── uploads/
│   └── chatbot/               # Temporary file storage
└── requirements_chatbot.txt   # Dependencies
```

## API Endpoints

### POST /api/chatbot/message
Send text message to chatbot
```json
{
  "message": "Your question here"
}
```

### POST /api/chatbot/image
Send image with optional message
```
FormData:
- image: File
- message: String (optional)
```

### POST /api/chatbot/file
Upload file for analysis
```
FormData:
- file: File
- message: String (optional)
```

### POST /api/chatbot/reset
Reset conversation history
```json
{}
```

## Browser Compatibility

### Voice Features
- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Limited voice recognition support

### Camera Features
- All modern browsers with camera permissions

### File Upload
- All modern browsers

## Customization

### Styling

The chatbot widget can be customized by modifying the CSS in `templates/chatbot_widget.html`:

```css
#chatbot-button {
    /* Change button color */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

#chatbot-window {
    /* Change window size */
    width: 380px;
    height: 550px;
}
```

### Position

To change the widget position, modify:

```css
#chatbot-widget {
    bottom: 20px;  /* Distance from bottom */
    right: 20px;   /* Distance from right */
}
```

### AI Model

To use a different Gemini model, update `gemini_chatbot.py`:

```python
self.model = genai.GenerativeModel('gemini-1.5-pro')  # More powerful model
```

## Troubleshooting

### Chatbot Not Appearing
1. Check browser console for errors
2. Verify `chatbot_widget.html` is included in `base.html`
3. Clear browser cache

### Voice Not Working
1. Check browser permissions for microphone
2. Ensure HTTPS connection (required for microphone access)
3. Try a different browser

### Camera Not Working
1. Check browser permissions for camera
2. Ensure HTTPS connection
3. Close other applications using the camera

### API Errors
1. Verify API key is valid
2. Check internet connection
3. Review API quota limits

## Security Considerations

### Production Deployment

1. **Move API Key to Environment Variables**:
```python
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

2. **Add Rate Limiting**:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: session.get('user_id'))

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
@limiter.limit("10 per minute")
def send_message():
    # ...
```

3. **Validate File Uploads**:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

4. **Sanitize User Input**:
```python
from bleach import clean
message = clean(data.get('message', ''))
```

## Advanced Features

### Custom Prompts

Add system prompts for specific contexts:

```python
def send_message(self, message, context="fitness"):
    prompts = {
        "fitness": "You are a fitness expert. ",
        "nutrition": "You are a nutrition specialist. "
    }
    full_message = prompts.get(context, "") + message
    response = self.chat.send_message(full_message)
    return response.text
```

### Conversation Memory

Store conversations in database:

```python
@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
def send_message():
    # ... existing code ...
    
    # Save to database
    db.conversations.insert_one({
        'user_id': session.get('user_id'),
        'message': message,
        'response': response,
        'timestamp': datetime.utcnow()
    })
```

## Performance Optimization

### Caching Responses

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(message):
    return chatbot.send_message(message)
```

### Async Processing

```python
import asyncio

async def send_message_async(message):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, chatbot.send_message, message)
    return response
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify all dependencies are installed
4. Test with the provided API key first

## License

This chatbot integration is part of the DeepFit AI project.

## Credits

- **AI Model**: Google Gemini API
- **Voice Recognition**: Web Speech API
- **Camera Access**: MediaDevices API
- **UI Framework**: Custom CSS with modern design
