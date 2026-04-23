# 🚀 Gemini Chatbot - Quick Start Guide

## ⚡ Fast Setup (3 Steps)

### Step 1: Install Dependencies
```bash
install_chatbot.bat
```
OR manually:
```bash
pip install google-generativeai Pillow
```

### Step 2: Test API Connection
```bash
python test_gemini_api.py
```

You should see:
```
✓ API key configured successfully
✓ Test successful!
✓ All tests passed!
```

### Step 3: Start Your App
```bash
python app.py
```

## ✅ Verify It's Working

1. Open your browser to `http://localhost:5000`
2. Look for the **purple chat icon** at bottom-right corner
3. Click it to open the chatbot
4. Type "Hello" and press Enter
5. You should get a response!

## 🎯 Features to Try

### 💬 Text Chat
- Type: "What exercises should I do?"
- Type: "Explain proper squat form"
- Type: "Calculate BMI for 70kg and 175cm"

### 🎤 Voice Input
1. Click the microphone icon (🎤)
2. Say your question
3. Click send

### 📷 Camera Analysis
1. Click the camera icon (📷)
2. Allow camera access
3. AI analyzes what it sees

### 📎 File Upload
1. Click the attachment icon (📎)
2. Select an image or document
3. Get AI analysis

## 🔧 If Something Goes Wrong

### Chatbot not appearing?
```bash
# Clear cache and restart
python app.py
```
Then hard refresh browser (Ctrl+F5)

### Getting errors?
```bash
# Run the test script
python test_gemini_api.py
```

### Still not working?
Check `CHATBOT_TROUBLESHOOTING.md` for detailed solutions.

## 📱 Mobile Usage

The chatbot works on mobile too!
- Responsive design
- Touch-friendly buttons
- Voice input on supported browsers

## 🎨 Customization

### Change Colors
Edit `templates/chatbot_widget.html`:
```css
#chatbot-button {
    background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);
}
```

### Change Position
```css
#chatbot-widget {
    bottom: 20px;  /* Distance from bottom */
    right: 20px;   /* Distance from right */
}
```

## 📊 What Models Are Being Used?

When you start the app, you'll see:
```
Using text model: gemini-pro
Using vision model: gemini-pro-vision
```

The chatbot automatically picks the best available models!

## 🔐 Security Note

For production:
1. Move API key to environment variable
2. Add rate limiting
3. Enable HTTPS

See `CHATBOT_README.md` for details.

## 💡 Pro Tips

1. **Clear History**: Click reset to start fresh conversation
2. **Voice Output**: Responses are automatically spoken
3. **Image Size**: Compress large images for faster processing
4. **File Limit**: Keep files under 5MB

## 🎉 You're All Set!

The chatbot is now integrated into every page of your app. Enjoy! 🚀

---

**Need Help?**
- 📖 Full docs: `CHATBOT_README.md`
- 🔧 Troubleshooting: `CHATBOT_TROUBLESHOOTING.md`
- 🧪 Test API: `python test_gemini_api.py`
