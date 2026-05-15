import cv2
import numpy as np
import mediapipe as mp
import base64
from typing import Tuple, Dict, List, Optional
import math
import logging

logger = logging.getLogger(__name__)


class FaceVerifier:
    """
    Robust Face Verification System using Mediapipe Landmarks.
    Compares face signatures with forgiving thresholds for real-world use.
    """

    def __init__(self, threshold: float = 0.70):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.threshold = threshold

        self.LANDMARKS = {
            'left_eye_outer': 33,
            'left_eye_inner': 133,
            'right_eye_outer': 362,
            'right_eye_inner': 263,
            'nose_tip': 1,
            'nose_bridge': 168,
            'mouth_left': 61,
            'mouth_right': 291,
            'mouth_top': 0,
            'mouth_bottom': 17,
            'chin': 152,
            'forehead': 10,
            'left_cheek': 234,
            'right_cheek': 454,
            'left_jaw': 58,
            'right_jaw': 288,
            'left_eyebrow_inner': 55,
            'right_eyebrow_inner': 285,
            'left_eyebrow_outer': 70,
            'right_eyebrow_outer': 300,
        }

    def decode_base64_image(self, base64_string: str) -> Optional[np.ndarray]:
        try:
            if not base64_string:
                logger.error("Empty base64 string provided")
                return None
            
            # Clean up the string
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Remove whitespace
            base64_string = "".join(base64_string.split())
            
            # Pad if necessary
            padding = len(base64_string) % 4
            if padding:
                base64_string += "=" * (4 - padding)
                
            img_data = base64.b64decode(base64_string)
            if not img_data:
                logger.error("Failed to decode base64 data")
                return None
                
            nparr = np.frombuffer(img_data, np.uint8)
            if nparr.size == 0:
                logger.error("Decoded buffer is empty")
                return None
                
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                logger.error("cv2.imdecode failed to create image")
                return None
                
            return img
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            return None

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        if image is None:
            return None
        try:
            # Resize for consistency
            h, w = image.shape[:2]
            if w > 800:
                scale = 800 / w
                image = cv2.resize(image, (800, int(h * scale)))
            
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            processed = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            return processed
        except Exception:
            return image

    def get_face_signature(self, image: np.ndarray) -> Optional[np.ndarray]:
        if image is None:
            return None
        processed = self.preprocess_image(image)
        results = self.mp_face_mesh.process(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            # Try without preprocessing if it failed
            results = self.mp_face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                logger.warning("No face detected in image")
                return None
        landmarks = results.multi_face_landmarks[0].landmark

        def get_dist(idx1, idx2):
            p1 = landmarks[idx1]
            p2 = landmarks[idx2]
            return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

        interpupillary = get_dist(self.LANDMARKS['left_eye_inner'], self.LANDMARKS['right_eye_inner'])
        if interpupillary == 0:
            logger.warning("Zero interpupillary distance detected")
            return None

        # Use interpupillary distance as the universal normalization factor
        # This makes all ratios relative to a stable biological constant
        norm = interpupillary

        # Enhanced signature with more ratios for better uniqueness
        signature = [
            get_dist(33, 133) / norm,                # left eye width
            get_dist(362, 263) / norm,               # right eye width
            get_dist(33, 362) / norm,                # eye outer to eye outer
            get_dist(133, 263) / norm,               # interpupillary (should be 1.0)
            get_dist(1, 168) / norm,                 # nose tip to bridge
            get_dist(1, 152) / norm,                 # nose tip to chin
            get_dist(10, 1) / norm,                  # forehead to nose tip
            get_dist(61, 291) / norm,                # mouth width
            get_dist(0, 17) / norm,                  # mouth height
            get_dist(58, 288) / norm,                # jaw width
            get_dist(1, 61) / norm,                  # nose tip to mouth left
            get_dist(1, 291) / norm,                 # nose tip to mouth right
            get_dist(55, 285) / norm,                # eyebrow inner distance
            get_dist(10, 168) / norm,                # forehead to bridge
            get_dist(70, 300) / norm,                # left eyebrow outer to right eyebrow outer
            get_dist(33, 70) / norm,                 # left eye to left eyebrow
            get_dist(362, 300) / norm,               # right eye to right eyebrow
            get_dist(133, 1) / norm,                 # left eye inner to nose tip
            get_dist(263, 1) / norm,                 # right eye inner to nose tip
            get_dist(152, 58) / norm,                # chin to left jaw
            get_dist(152, 288) / norm,               # chin to right jaw
            get_dist(234, 454) / norm,               # cheek distance (face width)
            get_dist(10, 152) / norm,                # forehead to chin (face height)
            get_dist(10, 152) / get_dist(234, 454),  # aspect ratio
        ]

        sig = np.array(signature, dtype=np.float32)
        
        # We NO LONGER use Z-score normalization per vector as it makes different faces
        # with similar relative proportions look identical.
        # Instead, we just return the raw ratios which are already scale-invariant.
        
        return sig

    def compute_similarity(self, sig1: np.ndarray, sig2: np.ndarray) -> Tuple[float, float]:
        if sig1 is None or sig2 is None:
            return 0.0, 10.0
            
        # Euclidean distance
        euclidean_dist = np.linalg.norm(sig1 - sig2)
        
        # Cosine similarity
        dot = np.dot(sig1, sig2)
        norm1 = np.linalg.norm(sig1)
        norm2 = np.linalg.norm(sig2)
        cosine_sim = dot / (norm1 * norm2) if norm1 > 1e-6 and norm2 > 1e-6 else 0

        # Euclidean score: mapped to 0-1 range. 
        # dist < 0.1 is very similar, dist > 0.4 is quite different.
        # Increased divisor to 0.8 for better real-world usability
        euclidean_score = max(0, 1.0 - (euclidean_dist / 0.8))
        
        # Cosine score: mapped from [-1, 1] to [0, 1]
        cosine_score = (cosine_sim + 1) / 2
        
        # Balanced combined score
        # Using 50/50 split to capture both shape (cosine) and scale (euclidean)
        combined_score = (0.5 * euclidean_score + 0.5 * cosine_score)

        logger.info(
            f"Similarity: combined={combined_score:.4f}, "
            f"dist={euclidean_dist:.4f}, cosine={cosine_sim:.4f}"
        )
        return combined_score, euclidean_dist

    def verify(self, reference_photo_base64: str, current_frame: np.ndarray) -> Tuple[bool, float, Dict]:
        debug_info = {
            'reference_decoded': False,
            'reference_face_found': False,
            'current_face_found': False,
            'distance': None,
            'similarity': None,
            'threshold': self.threshold
        }
        ref_img = self.decode_base64_image(reference_photo_base64)
        if ref_img is None:
            logger.error("Failed to decode reference photo")
            return False, 0.0, debug_info
        debug_info['reference_decoded'] = True
        ref_sig = self.get_face_signature(ref_img)
        if ref_sig is None:
            logger.error("No face detected in reference photo")
            return False, 0.0, debug_info
        debug_info['reference_face_found'] = True
        curr_sig = self.get_face_signature(current_frame)
        if curr_sig is None:
            logger.error("No face detected in current frame")
            return False, 0.0, debug_info
        debug_info['current_face_found'] = True
        similarity, distance = self.compute_similarity(ref_sig, curr_sig)
        debug_info['distance'] = float(distance)
        debug_info['similarity'] = float(similarity)
        is_match = bool(similarity >= self.threshold)
        confidence = float(similarity)
        logger.info(
            f"Verification: is_match={is_match}, confidence={confidence:.4f}, threshold={self.threshold}"
        )
        return is_match, confidence, debug_info

    def verify_from_base64(self, reference_photo_base64: str, current_photo_base64: str) -> Tuple[bool, float, Dict]:
        curr_img = self.decode_base64_image(current_photo_base64)
        if curr_img is None:
            logger.error("Failed to decode current photo")
            return False, 0.0, {'error': 'Failed to decode current photo'}
        return self.verify(reference_photo_base64, curr_img)
