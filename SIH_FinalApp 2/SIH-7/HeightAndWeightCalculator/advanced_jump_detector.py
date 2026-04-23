import cv2
import numpy as np
import mediapipe as mp
import time
import json
import os
from datetime import datetime
from collections import deque
from scipy.signal import savgol_filter
from sklearn.preprocessing import StandardScaler
import math
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class AdvancedJumpDetector:
    """State-of-the-art vertical jump detector using MediaPipe pose estimation"""
    
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Jump tracking
        self.jump_count = 0
        self.current_height_cm = 0.0
        self.max_height_cm = 0.0
        self.state = "ground"
        self.feedback = "System Ready"
        
        # Advanced tracking
        self.pose_history = deque(maxlen=120)  # 4 seconds at 30fps
        self.velocity_history = deque(maxlen=60)
        self.acceleration_history = deque(maxlen=30)
        
        # Calibration
        self.baseline_positions = deque(maxlen=90)  # 3 seconds
        self.pixels_per_cm = None
        self.is_calibrated = False
        self.calibration_frames = 0
        self.reference_height_cm = 170  # Default human height
        
        # Detection parameters
        self.jump_threshold_velocity = 50  # pixels/frame
        self.ground_threshold = 10  # pixels
        self.smoothing_window = 7
        
        # Data storage
        self.jump_history = []
        self.session_start = datetime.now()
        self.data_dir = "jump_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # MongoDB connection
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_collection = None
        self.init_mongodb()
        
        # Performance metrics
        self.frame_times = deque(maxlen=30)
    
    def init_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            self.mongo_client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
            self.mongo_client.admin.command('ping')
            self.mongo_db = self.mongo_client['sih2573']
            self.mongo_collection = self.mongo_db['Vertical_Jump']
            print("[OK] MongoDB connected successfully")
            print(f"Database: {self.mongo_db.name}")
            print(f"Collection: {self.mongo_collection.name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[WARNING] MongoDB connection failed: {e}")
            self.mongo_client = None
        
    def calculate_pixels_per_cm(self, landmarks):
        """Calculate pixels per cm using human body proportions"""
        if not landmarks:
            return None
            
        # Get key body points
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # Calculate shoulder width in pixels
        shoulder_width_px = math.sqrt(
            (left_shoulder.x - right_shoulder.x)**2 + 
            (left_shoulder.y - right_shoulder.y)**2
        )
        
        # Calculate body height in pixels (shoulder to ankle)
        avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        avg_ankle_y = (left_ankle.y + right_ankle.y) / 2
        body_height_px = abs(avg_ankle_y - avg_shoulder_y)
        
        # Human body proportions: shoulder width ≈ 24% of height
        estimated_height_cm = (shoulder_width_px / 0.24) if shoulder_width_px > 0 else self.reference_height_cm
        
        # Calculate pixels per cm
        if body_height_px > 0:
            return body_height_px / (estimated_height_cm * 0.75)  # 75% of height from shoulder to ankle
        
        return None
    
    def extract_pose_features(self, landmarks, frame_shape):
        """Extract comprehensive pose features"""
        if not landmarks:
            return None
            
        h, w = frame_shape[:2]
        
        # Key landmarks
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        
        # Convert to pixel coordinates
        features = {
            'timestamp': time.time(),
            'feet_center_y': ((left_ankle.y + right_ankle.y) / 2) * h,
            'feet_center_x': ((left_ankle.x + right_ankle.x) / 2) * w,
            'knee_center_y': ((left_knee.y + right_knee.y) / 2) * h,
            'hip_center_y': ((left_hip.y + right_hip.y) / 2) * h,
            'nose_y': nose.y * h,
            'body_angle': self.calculate_body_angle(landmarks),
            'knee_angle_left': self.calculate_joint_angle(left_hip, left_knee, left_ankle),
            'knee_angle_right': self.calculate_joint_angle(right_hip, right_knee, right_ankle),
            'confidence': min(left_ankle.visibility, right_ankle.visibility)
        }
        
        return features
    
    def calculate_body_angle(self, landmarks):
        """Calculate body lean angle"""
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        shoulder_center = ((left_shoulder.x + right_shoulder.x) / 2, (left_shoulder.y + right_shoulder.y) / 2)
        hip_center = ((left_hip.x + right_hip.x) / 2, (left_hip.y + right_hip.y) / 2)
        
        angle = math.atan2(hip_center[0] - shoulder_center[0], hip_center[1] - shoulder_center[1])
        return math.degrees(angle)
    
    def calculate_joint_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        a = np.array([point1.x, point1.y])
        b = np.array([point2.x, point2.y])
        c = np.array([point3.x, point3.y])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def calibrate_system(self, features):
        """Advanced calibration using pose data"""
        if not features or features['confidence'] < 0.7:
            return False
            
        self.calibration_frames += 1
        self.baseline_positions.append(features['feet_center_y'])
        
        if self.calibration_frames >= 90:  # 3 seconds
            # Calculate stable baseline
            baseline_array = np.array(self.baseline_positions)
            self.baseline_y = np.median(baseline_array)
            
            # Calculate noise level for adaptive thresholding
            noise_level = np.std(baseline_array)
            self.ground_threshold = max(10, noise_level * 2)
            
            self.is_calibrated = True
            self.feedback = "Calibrated! Ready to jump"
            return True
        else:
            progress = (self.calibration_frames / 90) * 100
            self.feedback = f"Calibrating... {progress:.0f}%"
            
        return False
    
    def detect_jump_advanced(self, features):
        """Advanced jump detection using multiple signals"""
        if not features or not self.is_calibrated:
            return
            
        # Store pose data
        self.pose_history.append(features)
        
        if len(self.pose_history) < 10:
            return
            
        # Calculate smoothed position
        recent_positions = [p['feet_center_y'] for p in list(self.pose_history)[-10:]]
        smoothed_position = np.mean(recent_positions)
        
        # Calculate velocity and acceleration
        if len(self.pose_history) >= 5:
            positions = [p['feet_center_y'] for p in list(self.pose_history)[-5:]]
            times = [p['timestamp'] for p in list(self.pose_history)[-5:]]
            
            # Velocity calculation
            velocity = (positions[-1] - positions[-3]) / (times[-1] - times[-3]) if len(positions) >= 3 else 0
            self.velocity_history.append(velocity)
            
            # Acceleration calculation
            if len(self.velocity_history) >= 3:
                velocities = list(self.velocity_history)[-3:]
                acceleration = (velocities[-1] - velocities[-3]) / 2
                self.acceleration_history.append(acceleration)
        
        # Height calculation
        height_diff = self.baseline_y - smoothed_position
        self.current_height_cm = max(0, height_diff / self.pixels_per_cm) if self.pixels_per_cm else 0
        
        # Advanced jump state machine
        current_velocity = self.velocity_history[-1] if self.velocity_history else 0
        
        if self.state == "ground":
            # Detect takeoff
            if (height_diff > self.ground_threshold and 
                current_velocity < -self.jump_threshold_velocity and
                features['confidence'] > 0.6):
                self.state = "takeoff"
                self.feedback = "Takeoff detected!"
                
        elif self.state == "takeoff":
            # Detect peak
            if current_velocity > -10:  # Velocity near zero at peak
                self.state = "peak"
                self.feedback = "Peak reached!"
                
        elif self.state == "peak":
            # Detect landing
            if (height_diff < self.ground_threshold * 1.5 and 
                current_velocity > 20):
                self.state = "ground"
                self.jump_count += 1
                
                # Calculate jump metrics
                jump_height = self.calculate_jump_height()
                if jump_height > self.max_height_cm:
                    self.max_height_cm = jump_height
                    
                self.feedback = f"Jump #{self.jump_count}: {jump_height:.1f}cm"
                self.save_jump_data(jump_height, features)
    
    def calculate_jump_height(self):
        """Calculate accurate jump height using multiple methods"""
        if len(self.pose_history) < 30:
            return self.current_height_cm
            
        # Method 1: Peak detection
        recent_heights = []
        for pose in list(self.pose_history)[-60:]:  # Last 2 seconds
            height = (self.baseline_y - pose['feet_center_y']) / self.pixels_per_cm if self.pixels_per_cm else 0
            recent_heights.append(max(0, height))
            
        if recent_heights:
            # Apply smoothing filter
            if len(recent_heights) >= 7:
                smoothed_heights = savgol_filter(recent_heights, 7, 3)
                peak_height = np.max(smoothed_heights)
            else:
                peak_height = np.max(recent_heights)
                
            return peak_height
            
        return self.current_height_cm
    
    def process_frame(self, frame):
        """Main processing function with advanced pose estimation"""
        start_time = time.time()
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Calculate pixels per cm if not set
            if self.pixels_per_cm is None:
                self.pixels_per_cm = self.calculate_pixels_per_cm(results.pose_landmarks.landmark)
                if self.pixels_per_cm is None:
                    self.pixels_per_cm = 3.0  # Fallback
            
            # Extract features
            features = self.extract_pose_features(results.pose_landmarks.landmark, frame.shape)
            
            if features:
                # Calibrate or detect jump
                if not self.is_calibrated:
                    self.calibrate_system(features)
                else:
                    self.detect_jump_advanced(features)
                
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                
                # Draw measurements
                self.draw_measurements(frame, features)
        else:
            self.feedback = "Person not detected - stand in view"
        
        # Draw UI
        self.draw_advanced_ui(frame)
        
        # Track performance
        processing_time = time.time() - start_time
        self.frame_times.append(processing_time)
        
        return frame
    
    def draw_measurements(self, frame, features):
        """Draw advanced measurements and indicators"""
        h, w = frame.shape[:2]
        
        if self.is_calibrated and self.baseline_y:
            # Draw baseline
            baseline_px = int(self.baseline_y)
            cv2.line(frame, (50, baseline_px), (w-50, baseline_px), (0, 255, 0), 2)
            cv2.putText(frame, "Ground Level", (55, baseline_px-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw height measurement
            feet_y = int(features['feet_center_y'])
            feet_x = int(features['feet_center_x'])
            
            if self.current_height_cm > 2:
                cv2.line(frame, (feet_x, baseline_px), (feet_x, feet_y), (255, 0, 255), 3)
                cv2.putText(frame, f"{self.current_height_cm:.1f}cm", 
                           (feet_x + 15, (baseline_px + feet_y)//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
            
            # Draw velocity indicator
            if self.velocity_history:
                velocity = self.velocity_history[-1]
                velocity_color = (0, 255, 0) if velocity < 0 else (0, 0, 255)
                cv2.putText(frame, f"Vel: {velocity:.1f}px/s", (feet_x + 15, feet_y - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, velocity_color, 2)
    
    def draw_advanced_ui(self, frame):
        """Draw compact user interface matching the reference image"""
        # Compact background for stats (smaller panel)
        panel_width = 280
        panel_height = 160
        cv2.rectangle(frame, (10, 10), (panel_width, panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (panel_width, panel_height), (255, 255, 255), 2)
        
        # Performance stats with smaller font
        avg_fps = 1.0 / np.mean(self.frame_times) if self.frame_times else 0
        
        stats = [
            f"Jumps: {self.jump_count}",
            f"Current: {self.current_height_cm:.1f}cm",
            f"Max: {self.max_height_cm:.1f}cm",
            f"State: {self.state.upper()}",
            f"Status: System Ready" if self.is_calibrated else "Calibrating...",
            f"FPS: {avg_fps:.1f}",
            f"Calibrated: {'YES' if self.is_calibrated else 'NO'}"
        ]
        
        for i, stat in enumerate(stats):
            color = (255, 255, 255)
            cv2.putText(frame, stat, (20, 30 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    def save_jump_data(self, height, features):
        """Save comprehensive jump data"""
        jump_data = {
            'timestamp': datetime.now().isoformat(),
            'height_cm': round(height, 2),
            'jump_number': self.jump_count,
            'body_angle': features['body_angle'],
            'knee_angles': {
                'left': features['knee_angle_left'],
                'right': features['knee_angle_right']
            },
            'confidence': features['confidence'],
            'pixels_per_cm': self.pixels_per_cm
        }
        self.jump_history.append(jump_data)
    
    def save_to_mongodb(self):
        """Save session data to MongoDB"""
        if not self.jump_history:
            print("[WARNING] No data to save")
            return False
        
        session_data = {
            'session_start': self.session_start.isoformat(),
            'total_jumps': self.jump_count,
            'max_height': self.max_height_cm,
            'average_height': sum(j['height_cm'] for j in self.jump_history) / len(self.jump_history),
            'calibration_data': {
                'pixels_per_cm': self.pixels_per_cm,
                'baseline_y': self.baseline_y
            },
            'jumps': self.jump_history
        }
        
        if self.mongo_client:
            try:
                result = self.mongo_collection.insert_one(session_data)
                print(f"[OK] Data saved to MongoDB: {result.inserted_id}")
                print(f"Database: USER, Collection: Vertical_Jump")
                return True
            except Exception as e:
                print(f"[ERROR] MongoDB save failed: {e}")
                print(f"Error details: {str(e)}")
        
        # Fallback to JSON
        try:
            filename = f"advanced_session_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"[OK] Fallback: Data saved to {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Save failed: {e}")
            return False
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        avg_height = 0
        if self.jump_history:
            avg_height = sum(j['height_cm'] for j in self.jump_history) / len(self.jump_history)
        
        return {
            'total_jumps': self.jump_count,
            'current_height': self.current_height_cm,
            'max_height': self.max_height_cm,
            'average_height': avg_height,
            'feedback': self.feedback,
            'state': self.state,
            'calibrated': self.is_calibrated,
            'pixels_per_cm': self.pixels_per_cm,
            'fps': 1.0 / np.mean(self.frame_times) if self.frame_times else 0
        }
    
    def reset_session(self):
        """Reset session with advanced cleanup"""
        self.jump_count = 0
        self.jump_history.clear()
        self.max_height_cm = 0.0
        self.current_height_cm = 0.0
        self.state = "ground"
        self.feedback = "Session Reset"
        self.pose_history.clear()
        self.velocity_history.clear()
        self.acceleration_history.clear()
        self.baseline_positions.clear()
        self.is_calibrated = False
        self.calibration_frames = 0
        self.pixels_per_cm = None