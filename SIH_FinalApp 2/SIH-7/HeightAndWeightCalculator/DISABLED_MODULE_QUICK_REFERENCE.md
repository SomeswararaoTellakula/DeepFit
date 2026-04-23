# Disabled Persons Assessment Module - Quick Reference

## Quick Start

### 1. Verify Installation
```bash
python test_disabled_module.py
```

### 2. Start Application
```bash
python app.py
```

### 3. Access Module
Navigate to: `http://localhost:5000/signup`
Click: "Disabled Persons" button

## Routes Reference

| Route | Method | Description |
|-------|--------|-------------|
| `/disabled_selection` | GET | Category selection page |
| `/blind_registration` | GET, POST | Registration form |
| `/blind_assessment` | GET | Assessment test page |
| `/api/save_blind_assessment` | POST | Save test results |
| `/blind_dashboard` | GET | View results |
| `/other_disabled_registration` | GET | Coming soon page |

## API Endpoints

### Save Blind Assessment
**Endpoint:** `/api/save_blind_assessment`  
**Method:** POST  
**Content-Type:** application/json

**Request Body:**
```json
{
  "audioReaction": [
    {
      "question": 1,
      "expected": "left",
      "response": "left",
      "correct": true,
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ],
  "audioQA": [
    {
      "question": "What skills are required...",
      "response": "User's answer...",
      "timestamp": "2025-01-15T10:35:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Assessment saved successfully"
}
```

## Session Variables

### blind_user
Stores registration data:
```python
{
  'name': str,
  'age': int,
  'gender': str,
  'photo': str (base64),
  'certificate': str (base64),
  'registration_time': str (ISO format)
}
```

### blind_results
Stores assessment results:
```python
{
  'audioReaction': {
    'accuracy': float,
    'avgTime': float
  },
  'audioQA': {
    'score': float,
    'answered': int
  },
  'overall': float
}
```

## Database Schema

### Collection: blind_assessments

```javascript
{
  _id: ObjectId,
  user_name: String,
  user_age: Number,
  user_gender: String,
  user_photo: String (base64),
  user_certificate: String (base64),
  audio_reaction_accuracy: Number,
  audio_reaction_avg_time: Number,
  audio_qa_score: Number,
  audio_qa_answered: Number,
  overall_score: Number,
  test_results: Object,
  assessment_date: Date,
  status: String
}
```

## JavaScript APIs Used

### Speech Synthesis (Text-to-Speech)
```javascript
const utterance = new SpeechSynthesisUtterance(text);
speechSynthesis.speak(utterance);
```

### Speech Recognition (Voice Input)
```javascript
const recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
};
recognition.start();
```

### Camera Access
```javascript
const stream = await navigator.mediaDevices.getUserMedia({ video: true });
video.srcObject = stream;
```

## Styling Classes

### Key CSS Classes
- `.selection-card` - Category selection cards
- `.registration-card` - Registration form container
- `.assessment-card` - Assessment test container
- `.test-status` - Current test status display
- `.question-display` - Question text display
- `.response-indicator` - User response feedback
- `.progress-bar` - Test progress indicator

## Common Issues & Solutions

### Issue: Camera not starting
**Solution:** Check browser permissions and use HTTPS or localhost

### Issue: Speech recognition not working
**Solution:** Use Chrome/Edge browser and check microphone permissions

### Issue: Session data lost
**Solution:** Ensure cookies are enabled and session is not expired

### Issue: Database connection error
**Solution:** Verify MongoDB is running on localhost:27017

## Testing Checklist

- [ ] Disabled Persons button visible on signup page
- [ ] Selection page displays both cards
- [ ] Registration form accepts all inputs
- [ ] Camera preview works
- [ ] Photo capture and retake works
- [ ] Certificate upload works
- [ ] Assessment page loads
- [ ] Introduction audio plays
- [ ] Audio reaction test works
- [ ] Voice recognition captures responses
- [ ] Q&A test works
- [ ] Progress bar updates
- [ ] Results save to database
- [ ] Dashboard displays all data

## Browser Compatibility

| Browser | Speech Synthesis | Speech Recognition | Camera |
|---------|-----------------|-------------------|--------|
| Chrome | ✓ | ✓ | ✓ |
| Edge | ✓ | ✓ | ✓ |
| Firefox | ✓ | ✗ | ✓ |
| Safari | ✓ | ✗ | ✓ |

**Recommended:** Chrome or Edge for full functionality

## Performance Tips

1. **Image Optimization:**
   - Compress photos before base64 encoding
   - Limit certificate file size to 5MB

2. **Audio Performance:**
   - Use short, clear audio messages
   - Implement audio caching

3. **Database:**
   - Index on user_email and assessment_date
   - Regular cleanup of old sessions

## Security Best Practices

1. **Input Validation:**
   - Sanitize all form inputs
   - Validate file types and sizes
   - Check age ranges

2. **Session Security:**
   - Use secure session cookies
   - Implement session timeout
   - Clear sensitive data after use

3. **Data Protection:**
   - Encrypt sensitive data at rest
   - Use HTTPS in production
   - Implement rate limiting

## Deployment Notes

### Production Checklist
- [ ] Set secure secret key
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up MongoDB authentication
- [ ] Implement logging
- [ ] Add error monitoring
- [ ] Set up backups
- [ ] Configure file upload limits

### Environment Variables
```bash
FLASK_SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=sih2573
UPLOAD_MAX_SIZE=5242880  # 5MB
```

## Support & Maintenance

### Logs Location
- Application logs: `logs/deepfit_YYYYMM.log`
- Error logs: Check Flask console output

### Monitoring
- Check MongoDB collections regularly
- Monitor session storage
- Track API response times
- Review error rates

### Updates
- Keep dependencies updated
- Test browser compatibility
- Review security patches
- Update documentation

---

**Quick Help:** Run `python test_disabled_module.py` to verify installation
**Documentation:** See DISABLED_PERSONS_MODULE_README.md for detailed guide
