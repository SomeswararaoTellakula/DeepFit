# Disabled Persons Assessment Module - Implementation Guide

## Overview

This module provides a comprehensive assessment system for disabled athletes, specifically designed for blind persons with plans to expand to other disability categories.

## Features Implemented

### 1. Enhanced Signup Page
- Added "Disabled Persons" button at the bottom of the signup page
- Styled with attractive UI and icon
- Positioned below "Already have an account? Login" text

### 2. Disabled Persons Selection Page
- Two large, animated cards for category selection:
  - **Blind Person**: For visually impaired athletes
  - **Deaf & Other Disabled**: For hearing impaired and other disabilities
- Modern CSS effects with hover animations
- Smooth transitions and gradient backgrounds

### 3. Blind Person Registration Flow

#### Registration Form (`/blind_registration`)
Fields included:
- Name (text input)
- Age (number input)
- Gender (dropdown: Male/Female/Other)
- Upload Disability Certificate (file upload - images/PDF)
- Capture Photo (camera access with live preview)

Features:
- Real-time camera preview
- Photo capture and retake functionality
- Form validation
- Responsive design

#### Assessment Test Page (`/blind_assessment`)
Automated test flow with:

**Introduction Audio:**
- Plays comprehensive guidelines
- 1-minute preparation time
- Camera surveillance notification
- Test rules and regulations

**Test 1: Audio Reaction Test**
- 3 questions testing directional sound recognition
- Sounds from: Left, Right, Top, Bottom
- Voice input for responses
- Measures:
  - Reaction time
  - Direction accuracy
  - Response quality

**Test 2: Audio Q&A Test**
- 5 comprehensive questions:
  1. Skills required to be a good athlete
  2. Factors affecting sports performance
  3. Team communication during matches
  4. Focus and confidence maintenance
  5. Handling challenging situations

Features:
- Text-to-speech for all questions
- Speech recognition for answers
- Real-time progress tracking
- Visual feedback for responses
- Automatic progression between tests

#### Dashboard Results Page (`/blind_dashboard`)
Displays:

**User Details:**
- Name, Age, Gender
- Captured photo
- Uploaded disability certificate

**Test Results:**
- Audio Reaction Test:
  - Accuracy percentage
  - Average response time
- Audio Q&A Test:
  - Evaluation score
  - Questions answered count
- Overall Performance Summary

### 4. Other Disabled Persons
- Placeholder page with "Coming Soon" message
- Professional design matching the theme
- Back navigation to selection page

## Technical Implementation

### Routes Added to app.py

```python
@app.route('/disabled_selection')
def disabled_selection()

@app.route('/blind_registration', methods=['GET', 'POST'])
def blind_registration()

@app.route('/blind_assessment')
def blind_assessment()

@app.route('/api/save_blind_assessment', methods=['POST'])
def save_blind_assessment()

@app.route('/blind_dashboard')
def blind_dashboard()

@app.route('/other_disabled_registration')
def other_disabled_registration()
```

### Database Collections

**blind_assessments** collection stores:
- User information (name, age, gender)
- Photo and certificate data (base64 encoded)
- Audio reaction test results
- Audio Q&A test results
- Overall scores and timestamps

### Session Management

Uses Flask session to store:
- `blind_user`: Registration data
- `blind_results`: Assessment results

### Technologies Used

1. **Frontend:**
   - HTML5 with Jinja2 templates
   - CSS3 with animations and gradients
   - JavaScript for interactivity
   - Web Speech API for text-to-speech
   - Web Speech Recognition API for voice input
   - MediaDevices API for camera access

2. **Backend:**
   - Flask routes and session management
   - MongoDB for data storage
   - Base64 encoding for images
   - JSON for data exchange

3. **APIs:**
   - Speech Synthesis API (text-to-speech)
   - Speech Recognition API (voice input)
   - getUserMedia API (camera access)

## User Flow

```
Signup Page
    ↓
Click "Disabled Persons" button
    ↓
Disabled Selection Page
    ↓
Select "Blind Person"
    ↓
Registration Form
    ↓
Fill details + Upload certificate + Capture photo
    ↓
Click "Create & Start Assessment"
    ↓
Assessment Test Page
    ↓
Introduction Audio (1 minute)
    ↓
Test 1: Audio Reaction (3 questions)
    ↓
Test 2: Audio Q&A (5 questions)
    ↓
Completion Audio
    ↓
Results Dashboard
```

## File Structure

```
templates/
├── disabled_selection.html          # Category selection page
├── blind_registration.html          # Registration form
├── blind_assessment.html            # Assessment test page
├── blind_dashboard.html             # Results dashboard
└── other_disabled_registration.html # Coming soon page

app.py                               # Main application with routes
test_disabled_module.py              # Installation verification script
```

## Testing the Implementation

1. **Run the test script:**
   ```bash
   python test_disabled_module.py
   ```

2. **Start the Flask application:**
   ```bash
   python app.py
   ```

3. **Navigate to signup page:**
   ```
   http://localhost:5000/signup
   ```

4. **Click "Disabled Persons" button**

5. **Test the flow:**
   - Select "Blind Person"
   - Fill registration form
   - Complete assessment tests
   - View results dashboard

## Browser Requirements

- Modern browser with:
  - Web Speech API support (Chrome, Edge recommended)
  - Camera access permissions
  - Microphone access permissions
  - JavaScript enabled

## Security Considerations

1. **Camera/Microphone Access:**
   - Requires user permission
   - Only active during assessment

2. **Data Storage:**
   - Images stored as base64 in database
   - Session-based authentication
   - Secure file uploads

3. **Input Validation:**
   - Form validation on client and server
   - File type restrictions for certificates
   - Age and gender validation

## Future Enhancements

1. **Deaf & Other Disabled Module:**
   - Visual-based assessments
   - Sign language recognition
   - Alternative input methods

2. **AI Integration:**
   - Gemini API for answer evaluation
   - Advanced scoring algorithms
   - Personalized feedback

3. **Analytics:**
   - Performance tracking over time
   - Comparative analysis
   - Progress reports

4. **Accessibility:**
   - Screen reader support
   - Keyboard navigation
   - High contrast modes

## Troubleshooting

### Camera Not Working
- Check browser permissions
- Ensure HTTPS or localhost
- Try different browser

### Speech Recognition Not Working
- Use Chrome or Edge browser
- Check microphone permissions
- Ensure quiet environment

### Database Errors
- Verify MongoDB is running
- Check connection string
- Ensure collections exist

## Support

For issues or questions:
1. Check browser console for errors
2. Verify all permissions are granted
3. Ensure MongoDB is connected
4. Review Flask logs for server errors

## Credits

Developed as part of the DeepFit AI system for the Sports Authority of India (SAI) to provide inclusive assessment tools for disabled athletes.

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Production Ready
