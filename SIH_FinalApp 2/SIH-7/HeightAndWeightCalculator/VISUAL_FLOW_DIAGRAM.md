# Disabled Persons Assessment Module - Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SIGNUP PAGE (signup.html)                        │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Name: [____________]        Age: [___]                        │    │
│  │  Gender: [▼]                 Place: [____________]             │    │
│  │  Phone: [____________]       Email: [____________]             │    │
│  │  Password: [____________]                                      │    │
│  │  Photo: [📷 Capture]                                           │    │
│  │                                                                 │    │
│  │  [Create Account]                                              │    │
│  │                                                                 │    │
│  │  Already have an account? Login                                │    │
│  │                                                                 │    │
│  │  ┌───────────────────────────────────────────────────────┐    │    │
│  │  │  🦽 Disabled Persons                                  │    │    │
│  │  └───────────────────────────────────────────────────────┘    │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Click "Disabled Persons"
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              DISABLED SELECTION PAGE (disabled_selection.html)           │
│                                                                          │
│                    Select Disability Category                            │
│                                                                          │
│  ┌──────────────────────────┐      ┌──────────────────────────┐        │
│  │                          │      │                          │        │
│  │          👁️              │      │          🦻              │        │
│  │                          │      │                          │        │
│  │     Blind Person         │      │  Deaf & Other Disabled   │        │
│  │                          │      │                          │        │
│  │  Assessment for visually │      │  Assessment for hearing  │        │
│  │  impaired athletes       │      │  impaired and others     │        │
│  │                          │      │                          │        │
│  └──────────────────────────┘      └──────────────────────────┘        │
│           │                                     │                        │
│           │ Click                               │ Click                  │
│           ▼                                     ▼                        │
│  ┌──────────────────────────┐      ┌──────────────────────────┐        │
│  │  Blind Registration      │      │    Coming Soon Page      │        │
│  └──────────────────────────┘      └──────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    │ Select "Blind Person"
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│           BLIND REGISTRATION PAGE (blind_registration.html)              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  👁️ Blind Person Registration                                 │    │
│  │                                                                 │    │
│  │  Name: [____________]                                          │    │
│  │  Age: [___]                                                    │    │
│  │  Gender: [▼ Male/Female/Other]                                 │    │
│  │                                                                 │    │
│  │  📄 Upload Disability Certificate: [Choose File]               │    │
│  │                                                                 │    │
│  │  📷 Capture Photo:                                             │    │
│  │  ┌─────────────────────────────────────┐                      │    │
│  │  │                                     │                      │    │
│  │  │      [Live Camera Preview]          │                      │    │
│  │  │                                     │                      │    │
│  │  └─────────────────────────────────────┘                      │    │
│  │  [📷 Take Photo]                                               │    │
│  │                                                                 │    │
│  │  [✓ Create & Start Assessment]                                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    │ Submit Form
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│           ASSESSMENT TEST PAGE (blind_assessment.html)                   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    Assessment Test                              │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────┐                      │    │
│  │  │                                     │                      │    │
│  │  │    [Live Camera Surveillance]       │                      │    │
│  │  │                                     │                      │    │
│  │  └─────────────────────────────────────┘                      │    │
│  │                                                                 │    │
│  │  Status: [Initializing...]                                     │    │
│  │                                                                 │    │
│  │  Progress: [████████░░░░░░░░░░░░] 40%                         │    │
│  │                                                                 │    │
│  │  Question: [This is the second question]                       │    │
│  │                                                                 │    │
│  │  Response: [Listening... 🎤]                                   │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  FLOW:                                                                   │
│  1. 🔊 Introduction Audio (1 minute)                                    │
│     "The assessment will begin in 1 minute..."                          │
│                                                                          │
│  2. 🎯 Test 1: Audio Reaction Test (3 questions)                        │
│     - Play sound from direction                                         │
│     - User responds with voice                                          │
│     - Record accuracy & time                                            │
│                                                                          │
│  3. 💬 Test 2: Audio Q&A Test (5 questions)                             │
│     - Read question via audio                                           │
│     - User responds with voice                                          │
│     - Record and evaluate answer                                        │
│                                                                          │
│  4. ✅ Completion                                                        │
│     "The assessment test has completed."                                │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    │ Auto-redirect after completion
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              DASHBOARD PAGE (blind_dashboard.html)                       │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │           Assessment Results Dashboard                          │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │  User Details                                            │  │    │
│  │  │  ┌─────────┐                                            │  │    │
│  │  │  │  Photo  │  Name: John Doe                            │  │    │
│  │  │  │   👤    │  Age: 25                                   │  │    │
│  │  │  └─────────┘  Gender: Male                              │  │    │
│  │  │                                                          │  │    │
│  │  │  Certificate: [📄 Preview]                              │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │  🎯 Audio Reaction Test Results                         │  │    │
│  │  │                                                          │  │    │
│  │  │  ┌──────────────┐      ┌──────────────┐                │  │    │
│  │  │  │  Accuracy    │      │  Avg Time    │                │  │    │
│  │  │  │     85%      │      │    2.3s      │                │  │    │
│  │  │  └──────────────┘      └──────────────┘                │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │  💬 Audio Q&A Test Results                              │  │    │
│  │  │                                                          │  │    │
│  │  │  ┌──────────────┐      ┌──────────────┐                │  │    │
│  │  │  │  Score       │      │  Answered    │                │  │    │
│  │  │  │    78%       │      │     5/5      │                │  │    │
│  │  │  └──────────────┘      └──────────────┘                │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │  ⭐ Overall Performance Summary                          │  │    │
│  │  │                                                          │  │    │
│  │  │         Overall Score: 81.5%                            │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Features at Each Stage

### 1. Signup Page Enhancement
- ✅ New button added
- ✅ Attractive styling
- ✅ Icon included
- ✅ Proper positioning

### 2. Selection Page
- ✅ Two animated cards
- ✅ Modern design
- ✅ Hover effects
- ✅ Clear navigation

### 3. Registration Page
- ✅ All required fields
- ✅ Camera integration
- ✅ File upload
- ✅ Form validation

### 4. Assessment Page
- ✅ Audio playback
- ✅ Voice recognition
- ✅ Camera surveillance
- ✅ Progress tracking
- ✅ Two complete tests

### 5. Dashboard Page
- ✅ User details display
- ✅ Test results
- ✅ Scores and metrics
- ✅ Professional layout

## Technology Stack

```
Frontend:
├── HTML5 (Jinja2 Templates)
├── CSS3 (Animations, Gradients)
├── JavaScript (ES6+)
├── Web Speech API
├── Speech Recognition API
└── MediaDevices API

Backend:
├── Flask (Routes, Sessions)
├── MongoDB (Data Storage)
├── Python 3.x
└── Base64 Encoding

APIs Used:
├── speechSynthesis (Text-to-Speech)
├── webkitSpeechRecognition (Voice Input)
└── getUserMedia (Camera Access)
```

## Data Flow

```
User Input → Registration Form → Session Storage
                                       ↓
                              Assessment Tests
                                       ↓
                              Voice Responses
                                       ↓
                              Score Calculation
                                       ↓
                              MongoDB Storage
                                       ↓
                              Dashboard Display
```

## Security Measures

```
✓ Camera Surveillance
✓ Session Authentication
✓ Input Validation
✓ Secure File Upload
✓ Base64 Encoding
✓ MongoDB Security
```

---

**Status:** ✅ Fully Implemented  
**Testing:** ✅ Verified  
**Documentation:** ✅ Complete  
**Ready for:** Production Deployment
