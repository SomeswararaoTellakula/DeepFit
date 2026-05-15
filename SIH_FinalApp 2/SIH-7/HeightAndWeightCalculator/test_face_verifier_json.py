import cv2
import numpy as np
from face_verifier import FaceVerifier
import json

def test_face_verifier():
    verifier = FaceVerifier(threshold=0.45)
    
    # Create a dummy image (black image)
    # MediaPipe will likely fail to find a face, which is fine for testing the return type
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Test verify with an image where no face is detected
    is_match, confidence, debug_info = verifier.verify("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==", img)
    
    print(f"is_match type: {type(is_match)}")
    print(f"confidence type: {type(confidence)}")
    
    result = {
        'is_match': is_match,
        'confidence': confidence,
        'debug_info': debug_info
    }
    
    try:
        json_str = json.dumps(result)
        print("Successfully serialized to JSON")
        print(json_str)
    except TypeError as e:
        print(f"JSON serialization failed: {e}")

if __name__ == "__main__":
    test_face_verifier()
