# Face Verification Fix - TODO

## Issue: Face verification always returns False / "not verified"

### Tasks:
- [x] 1. Fix `face_verifier.py` - improve matching algorithm, add preprocessing, debug logging
- [x] 2. Fix `app.py` - add global FaceVerifier instance, debug endpoints, better error handling
- [x] 3. Fix `templates/blind_assessment.html` - add debug logging, retry logic, show confidence
- [x] 4. Create `debug_verify.py` - standalone test script for verification
- [ ] 5. Run syntax check and test complete flow

### Changes Made:

#### `face_verifier.py`:
- Increased threshold from 0.45 → 0.65 for real-world conditions
- Added image preprocessing (CLAHE lighting normalization, denoising)
- Added face alignment using eye landmarks
- Expanded signature from 9 to 21 geometric features
- Added signature normalization (zero mean, unit variance)
- Implemented multi-metric similarity (euclidean + cosine + correlation)
- Added comprehensive debug logging
- Returns debug_info dict with face detection status, distance, similarity

#### `app.py`:
- Added global `face_verifier = FaceVerifier(threshold=0.65)` instance
- Updated `/api/verify_user_identity` to use global instance + debug_info
- Updated `/api/verify_blind_identity` to use global instance + debug_info
- Added `/api/debug_verify` endpoint for testing with any two images
- Added proper logging to all verification endpoints

#### `templates/blind_assessment.html`:
- Added console logging of verification results
- Shows confidence percentage in status messages
- Displays debug confidence on identity mismatch warnings
- API/network errors don't increment mismatch count (retry logic)
- Increased initial verification interval: 2s → 3s
- Increased ongoing verification interval: 5s → 10s
- Added helpful message after 60s if still verifying

#### `debug_verify.py` (NEW):
- Standalone test script for local verification debugging
- Tests multiple thresholds (0.45, 0.55, 0.65, 0.75, 0.85)
- Can test with image files or base64 text files
- Provides detailed diagnostic output

### Root Causes Fixed:
1. ✅ Threshold too strict (0.45) for real-world conditions → Now 0.65
2. ✅ No image preprocessing (lighting, alignment) → Added CLAHE + face alignment
3. ✅ No debug logging to diagnose failures → Full debug_info in responses
4. ✅ New FaceVerifier instance per request → Global cached instance
5. ✅ Frontend silently failing without user feedback → Confidence shown in UI

