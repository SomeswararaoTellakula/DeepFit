import cv2
import mediapipe as mp
import numpy as np
import time

class AdvancedJumpDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Jump detection variables
        self.baseline_y = None
        self.calibrated = False
        self.calibration_frames = []
        self.jump_count = 0
        self.current_height = 0.0
        self.max_height = 0.0
        self.state = "GROUND"
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Thresholds
        self.jump_threshold = 15  # pixels
        self.landing_threshold = 5  # pixels
        
    def get_hip_center(self, landmarks, frame_width, frame_height):
        """Get center point between hips"""
        left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
        
        if left_hip.visibility > 0.5 and right_hip.visibility > 0.5:
            center_x = (left_hip.x + right_hip.x) / 2 * frame_width
            center_y = (left_hip.y + right_hip.y) / 2 * frame_height
            return int(center_x), int(center_y)
        return None
    
    def calibrate(self, hip_y):
        """Calibrate baseline position"""
        if len(self.calibration_frames) < 30:
            self.calibration_frames.append(hip_y)
            return False
        else:
            self.baseline_y = np.mean(self.calibration_frames)
            self.calibrated = True
            return True
    
    def detect_jump(self, hip_y):
        """Detect jump based on hip position"""
        if not self.calibrated or self.baseline_y is None:
            return
        
        # Calculate height difference in cm (approximate)
        height_diff = self.baseline_y - hip_y
        self.current_height = max(0, height_diff * 0.1)  # Convert to cm approximation
        
        # State machine for jump detection
        if self.state == "GROUND" and height_diff > self.jump_threshold:
            self.state = "JUMPING"
            self.jump_count += 1
            
        elif self.state == "JUMPING":
            if self.current_height > self.max_height:
                self.max_height = self.current_height
            
            if height_diff < self.landing_threshold:
                self.state = "GROUND"
    
    def update_fps(self):
        """Update FPS calculation"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.fps = self.frame_count / elapsed
    
    def get_status(self):
        """Get current status information"""
        return {
            'jumps': self.jump_count,
            'current': f"{self.current_height:.1f}cm",
            'max': f"{self.max_height:.1f}cm",
            'state': self.state,
            'status': "System Ready" if self.calibrated else "Calibrating...",
            'fps': f"{self.fps:.1f}",
            'calibrated': "YES" if self.calibrated else "NO"
        }