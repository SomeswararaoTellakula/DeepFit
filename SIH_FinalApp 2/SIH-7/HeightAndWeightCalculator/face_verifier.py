import cv2
import numpy as np
import mediapipe as mp
import base64
from typing import Tuple, Dict, List, Optional
import math

class FaceVerifier:
    """
    Lightweight Face Verification System using Mediapipe Landmarks.
    Compares face signatures based on geometric proportions.
    """
    
    def __init__(self, threshold: float = 0.45):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.threshold = threshold
        
        # Key landmark indices for signature calculation
        # These are based on Mediapipe Face Mesh indices
        self.LANDMARKS = {
            'left_eye': [33, 133],
            'right_eye': [362, 263],
            'nose_tip': 1,
            'mouth_corners': [61, 291],
            'chin': 152,
            'forehead': 10,
            'left_cheek': 234,
            'right_cheek': 454
        }

    def decode_base64_image(self, base64_string: str) -> Optional[np.ndarray]:
        """Decode base64 image string to OpenCV BGR image"""
        try:
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            img_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error decoding base64 image: {e}")
            return None

    def get_face_signature(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract a geometric signature from a face image.
        The signature consists of normalized distance ratios between key landmarks.
        """
        if image is None:
            return None
            
        results = self.mp_face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
            
        landmarks = results.multi_face_landmarks[0].landmark
        
        def get_dist(idx1, idx2):
            p1 = landmarks[idx1]
            p2 = landmarks[idx2]
            return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

        # Calculate base distances for normalization
        face_width = get_dist(self.LANDMARKS['left_cheek'], self.LANDMARKS['right_cheek'])
        face_height = get_dist(self.LANDMARKS['forehead'], self.LANDMARKS['chin'])
        
        if face_width == 0 or face_height == 0:
            return None
            
        # Signature: Ratios of distances to normalize for scale and distance from camera
        signature = [
            get_dist(33, 133) / face_width,             # Left eye width ratio
            get_dist(362, 263) / face_width,            # Right eye width ratio
            get_dist(33, 362) / face_width,             # Inter-eye distance ratio
            get_dist(61, 291) / face_width,             # Mouth width ratio
            get_dist(1, 152) / face_height,             # Nose to chin ratio
            get_dist(10, 1) / face_height,              # Forehead to nose ratio
            get_dist(1, 61) / face_width,               # Nose to mouth corner ratio
            get_dist(1, 234) / face_width,              # Nose to left cheek ratio
            get_dist(33, 61) / face_height,             # Eye to mouth ratio
        ]
        
        return np.array(signature)

    def verify(self, reference_photo_base64: str, current_frame: np.ndarray) -> Tuple[bool, float]:
        """
        Compare current frame face with reference photo.
        Returns (is_match, similarity_score)
        """
        ref_img = self.decode_base64_image(reference_photo_base64)
        if ref_img is None:
            return False, 0.0
            
        ref_sig = self.get_face_signature(ref_img)
        curr_sig = self.get_face_signature(current_frame)
        
        if ref_sig is None or curr_sig is None:
            return False, 0.0
            
        # Calculate Euclidean distance between signatures
        dist = np.linalg.norm(ref_sig - curr_sig)
        
        # Calculate confidence (inverse of distance, normalized)
        # 0.0 distance = 1.0 confidence
        confidence = max(0, 1.0 - (dist / (self.threshold * 2)))
        
        is_match = dist < self.threshold
        return is_match, confidence

    def verify_from_base64(self, reference_photo_base64: str, current_photo_base64: str) -> Tuple[bool, float]:
        """Helper to verify two base64 images"""
        curr_img = self.decode_base64_image(current_photo_base64)
        if curr_img is None:
            return False, 0.0
        return self.verify(reference_photo_base64, curr_img)
