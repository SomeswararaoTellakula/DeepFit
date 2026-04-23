# Blind Assessment Test - Quick Testing Guide

## 🚀 START TESTING

### Step 1: Start Application
```bash
cd "c:\Users\arunc\Videos\SIH_FinalApp( DeepFitAI Final-Project)\SIH_FinalApp\SIH-7\HeightAndWeightCalculator"
python app.py
```

### Step 2: Navigate to Assessment
1. Open browser: http://localhost:5000/signup
2. Click "Disabled Persons" button
3. Select "Blind Person"
4. Fill registration form
5. Upload certificate
6. Capture photo
7. Click "Create & Start Assessment"

---

## ✅ WHAT TO EXPECT

### Phase 1: Introduction (60 seconds)
- ✓ Camera feed appears
- ✓ Face detection starts (green rectangle around face)
- ✓ Audio plays: "The assessment will begin in 1 minute..."
- ✓ Complete guidelines spoken

### Phase 2: Test Introduction (5 seconds)
- ✓ Status: "Test 1: Audio Reaction Test"
- ✓ Audio: "First test is Audio Reaction Test..."
- ✓ Score display: "Score: 0/3"

### Phase 3: Question 1
- ✓ Audio: "Guess the direction of the sound for the first attempt"
- ✓ Directional sound plays (e.g., from left speaker)
- ✓ Screen shows: "Correct Answer: LEFT SIDE"
- ✓ Timer appears: "10" and counts down
- ✓ Timer turns orange at 5s, red at 3s
- ✓ Say "left" (or correct direction)
- ✓ Response captured: "You said: left"
- ✓ Result shown: "✓ Correct!" or "✗ Incorrect"
- ✓ Score updates if correct
- ✓ Audio: "Time completed for Question 1"

### Phase 4: Question 2
- ✓ Same process as Question 1
- ✓ Audio: "...for the second attempt"
- ✓ Different direction sound
- ✓ Progress bar: 66.67%

### Phase 5: Question 3
- ✓ Same process as Question 1
- ✓ Audio: "...for the third attempt"
- ✓ Different direction sound
- ✓ Progress bar: 100%

### Phase 6: Completion
- ✓ Audio: "The assessment test has completed"
- ✓ Status: "Assessment Complete!"
- ✓ Auto-redirect to dashboard (3 seconds)

---

## 🎯 FACE DETECTION TEST

### Test Face Loss:
1. During any question, move face out of camera view
2. **Expected:**
   - Screen turns red with pulse
   - Large warning: "FACE NOT VISIBLE"
   - Audio: "Face not visible"
   - Timer stops
   - Test pauses

### Test Face Restore:
1. Move face back into camera view
2. **Expected:**
   - Red screen clears
   - Warning disappears
   - Timer resumes
   - Test continues

---

## 🗣️ VOICE COMMANDS TO TEST

### Valid Commands:
- "left" or "left side" → Accepted
- "right" or "right side" → Accepted
- "top" or "up" → Accepted
- "bottom" or "down" → Accepted

### Invalid Commands:
- "middle" → Rejected
- "center" → Rejected
- Random words → Rejected
- **Expected:** "Invalid response. Please say: left, right, top, or bottom"

---

## ⏱️ TIMER TEST

### Normal Flow:
1. Timer starts at 10
2. Counts down: 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0
3. Color changes:
   - 10-6: Green
   - 5-4: Orange (pulse)
   - 3-0: Red (faster pulse)

### Time Expiry:
1. Don't respond to question
2. Wait for timer to reach 0
3. **Expected:**
   - Audio: "Time completed for Question X"
   - Question marked as "No response"
   - Moves to next question

---

## 💾 DATABASE VERIFICATION

### Check MongoDB:
1. Open MongoDB Compass
2. Connect: mongodb://localhost:27017/
3. Database: sih2573
4. Collection: "Blind details"

### Verify Data:
```javascript
{
  user_name: "Test User",
  user_age: 25,
  user_gender: "Male",
  audio_reaction_results: [
    {
      questionNumber: 1,
      correctAnswer: "left",
      userResponse: "left",
      correct: true,
      timeUsed: 3,
      timestamp: "2025-01-15T..."
    },
    // ... 2 more questions
  ],
  face_detection_logs: [
    {
      timestamp: "2025-01-15T...",
      status: "face_lost",
      currentQuestion: 2,
      timeRemaining: 7
    },
    {
      timestamp: "2025-01-15T...",
      status: "face_restored",
      currentQuestion: 2,
      timeRemaining: 7
    }
  ],
  final_score: 2,
  total_questions: 3,
  accuracy: 66.67,
  assessment_date: ISODate("2025-01-15T..."),
  status: "completed"
}
```

---

## 🎧 AUDIO TESTING

### Directional Sound Test:
1. **Use headphones** for best results
2. Question with "left" direction:
   - Sound should come from left speaker
3. Question with "right" direction:
   - Sound should come from right speaker
4. Question with "top" or "bottom":
   - Sound should be centered

### Audio Clarity:
- All speech should be clear
- No distortion
- Appropriate volume
- Proper pacing

---

## 📊 SCORING TEST

### Test Scenario 1: All Correct
- Answer all 3 questions correctly
- **Expected:** Score: 3/3, Accuracy: 100%

### Test Scenario 2: Mixed Results
- Q1: Correct
- Q2: Incorrect
- Q3: Correct
- **Expected:** Score: 2/3, Accuracy: 66.67%

### Test Scenario 3: All Incorrect
- Answer all 3 questions incorrectly
- **Expected:** Score: 0/3, Accuracy: 0%

### Test Scenario 4: Timeout
- Don't respond to questions
- **Expected:** Score: 0/3, Accuracy: 0%

---

## 🐛 TROUBLESHOOTING

### Camera Not Working:
- Check browser permissions
- Allow camera access
- Refresh page

### Microphone Not Working:
- Check browser permissions
- Allow microphone access
- Use Chrome or Edge

### Face Detection Not Working:
- Ensure good lighting
- Face camera directly
- Remove obstructions
- Check MediaPipe loaded

### Audio Not Playing:
- Check system volume
- Check browser audio settings
- Try different browser

### Directional Sound Not Working:
- Use headphones
- Check stereo output
- Test with music first

---

## ✅ SUCCESS CRITERIA

### Complete Test Run:
- [x] Introduction audio plays
- [x] Camera shows face with green box
- [x] All 3 questions asked
- [x] Directional sounds play correctly
- [x] Timer counts down properly
- [x] Voice recognition works
- [x] Responses validated correctly
- [x] Score calculated accurately
- [x] Face detection pauses test
- [x] Test resumes when face visible
- [x] Data saved to MongoDB
- [x] Dashboard shows results

### Database Check:
- [x] Document created in "Blind details"
- [x] All fields present
- [x] audio_reaction_results has 3 items
- [x] face_detection_logs has events
- [x] Scores calculated correctly
- [x] Timestamps recorded

---

## 📝 TEST REPORT TEMPLATE

```
Test Date: ___________
Tester: ___________

PHASE 1 - Introduction:
[ ] Audio played correctly
[ ] Camera started
[ ] Face detected

PHASE 2 - Questions:
[ ] Question 1 completed
[ ] Question 2 completed
[ ] Question 3 completed
[ ] Directional sounds correct
[ ] Timer worked properly
[ ] Voice recognition accurate

PHASE 3 - Face Detection:
[ ] Face loss detected
[ ] Test paused
[ ] Warning displayed
[ ] Audio alert played
[ ] Test resumed on face restore

PHASE 4 - Data Storage:
[ ] Data saved to MongoDB
[ ] All fields present
[ ] Scores correct
[ ] Logs recorded

PHASE 5 - Dashboard:
[ ] Redirected successfully
[ ] Results displayed
[ ] Scores shown correctly

ISSUES FOUND:
_______________________
_______________________

OVERALL STATUS: [ ] PASS [ ] FAIL
```

---

## 🎉 EXPECTED FINAL RESULT

After completing all tests:
1. ✅ All 3 questions answered
2. ✅ Score calculated (0-3)
3. ✅ Data in MongoDB "Blind details" collection
4. ✅ Dashboard shows results
5. ✅ Face detection logs recorded
6. ✅ All timestamps captured

**Status:** READY FOR PRODUCTION TESTING

---

**Quick Start:** `python app.py` → Navigate to signup → Test flow
**Database:** MongoDB Compass → sih2573 → "Blind details"
**Browser:** Chrome or Edge (recommended)
**Audio:** Use headphones for directional sound testing
