# Fix Plan: Face Verification & Blind Assessment Camera

## A. Fix face_verifier.py
- [x] Remove hardcoded `is_match = True`
- [x] Remove forced `confidence = max(0.85, confidence)`
- [x] Implement proper Euclidean distance matching against threshold (0.45)
- [x] Return False with low confidence when no face detected
- [x] Return actual computed confidence score

## B. Fix templates/blind_assessment.html
- [x] Add try/catch around camera.start()
- [x] Add user-facing error messages for camera failure
- [x] Add MediaPipe script-load detection
- [x] Add camera permission denied handler
- [x] Add retry button for camera initialization
- [x] Normalize canvas sizing with actual video dimensions

## Status: COMPLETE

