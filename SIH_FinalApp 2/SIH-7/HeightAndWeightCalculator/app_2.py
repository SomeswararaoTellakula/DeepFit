import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from typing import Tuple, Dict, List, Optional
import mediapipe as mp
from dataclasses import dataclass
import time
import threading
from queue import Queue
import os
import json
import glob
from datetime import datetime
import warnings
import winsound  # For buzzer sound on Windows
from enum import Enum
import math

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)
warnings.filterwarnings('ignore', category=FutureWarning)

class DetectionStatus(Enum):
    HUMAN_DETECTED = "human_detected"
    NO_HUMAN = "no_human"
    PARTIAL_BODY = "partial_body"
    GOOD_POSITION = "good_position"
    MEASURING_STABLE = "measuring_stable"
    AUTO_SAVED = "auto_saved"

@dataclass
class MeasurementResult:
    height_cm: float
    weight_kg: float
    confidence_score: float
    uncertainty_height: float
    uncertainty_weight: float
    processing_time_ms: float
    detection_status: DetectionStatus = DetectionStatus.GOOD_POSITION
    position_message: str = "Ready for measurement"
    stability_frames: int = 0
    is_auto_saved: bool = False

class AdvancedHeightWeightEstimator:
    """
    Enhanced Height and Weight Estimation System with visual guidance
    Features improved camera calibration and positioning overlays
    """
    
    def __init__(self, use_gpu: bool = True, use_depth_camera: bool = False):
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        self.use_depth_camera = use_depth_camera
        
        # Initialize models and components
        self._initialize_models()
        self._initialize_calibration()
        self._initialize_processors()
        
        # Camera calibration parameters - will be updated during runtime
        self.frame_width = 1280
        self.frame_height = 720
        self.camera_height_cm = 140  # Default camera height from ground
        self.subject_distance_cm = 250  # Optimal subject distance (2.5m)
        
        # Visual guidance parameters
        self.show_guidance_overlay = True
        self.guidance_alpha = 0.6
        
        # Auto-save parameters
        self.auto_save_enabled = True
        self.stability_threshold = 8  # Increased for better accuracy
        self.max_stability_frames = 12
        self.stability_tolerance_height = 1.0  # Tightened for accuracy
        self.stability_tolerance_weight = 0.8  # Tightened for accuracy
        self.auto_save_cooldown = 10.0
        self.should_close_after_save = False
        self.save_display_start = 0
        
        print(f"Enhanced System initialized on {self.device}")
        print(f"Camera calibration: {self.frame_width}x{self.frame_height}")
        print(f"Recommended setup: Camera at {self.camera_height_cm}cm height, subject at {self.subject_distance_cm}cm distance")
    
    def _initialize_models(self):
        """Initialize all AI models and preprocessing components"""
        
        # Enhanced Pose Detection with higher accuracy
        self.mp_holistic = mp.solutions.holistic.Holistic(
            min_detection_confidence=0.85,  # Increased for better accuracy
            min_tracking_confidence=0.8,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False,
            refine_face_landmarks=True
        )
        
        self.mp_pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.85,
            min_tracking_confidence=0.8,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False
        )
        
        # Enhanced Face Detection for better reference scaling
        self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.85
        )
        
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        
        # Drawing utilities
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        print("Models initialized with enhanced accuracy settings")
    
    def _initialize_calibration(self):
        """Initialize enhanced camera calibration parameters"""
        # These will be dynamically updated based on face detection
        self.camera_matrix = None
        self.dist_coeffs = np.zeros(4, dtype=np.float32)
        
        # Enhanced reference objects with precise measurements
        self.reference_objects = {
            'face_width_male': 14.2,       # More conservative estimate
            'face_width_female': 12.8,     # More conservative estimate  
            'face_height': 18.5,           # Nose to chin
            'interpupillary_distance': 6.2, # Eye to eye distance
            'head_height': 23.0,           # Top of head to chin
            'average_face_width': 13.5     # Gender-neutral average
        }
        
        # Measurement history with longer memory for better accuracy
        self.height_history = []
        self.weight_history = []
        self.confidence_history = []
        self.pixel_ratio_history = []
        
        # Enhanced stability tracking
        self.stable_measurements = []
        self.last_auto_save = 0
        self.consecutive_stable_frames = 0
        
        # Position tracking
        self.last_detection_time = 0
        self.no_human_count = 0
        self.buzzer_cooldown = 0
        
        # Body visibility tracking
        self.body_parts_status = {
            'head': False,
            'shoulders': False,
            'arms': False,
            'torso': False,
            'hips': False,
            'legs': False,
            'feet': False
        }
        
        # Guidance system
        self.guidance_zones = self._calculate_guidance_zones()
        
    def _initialize_processors(self):
        """Initialize processing components"""
        self.frame_queue = Queue(maxsize=3)
        self.result_queue = Queue(maxsize=3)
        self.processing_thread = None
        self.is_processing = False
    
    def _calculate_guidance_zones(self):
        """Calculate guidance zones for proper positioning"""
        # Define zones as percentages of frame
        return {
            'head_zone': {'y_min': 0.05, 'y_max': 0.25, 'x_center': 0.5, 'width': 0.3},
            'body_zone': {'y_min': 0.15, 'y_max': 0.95, 'x_center': 0.5, 'width': 0.4},
            'feet_zone': {'y_min': 0.85, 'y_max': 0.98, 'x_center': 0.5, 'width': 0.35},
            'optimal_subject_box': {'x_min': 0.3, 'x_max': 0.7, 'y_min': 0.05, 'y_max': 0.95}
        }
    
    def calibrate_camera_with_face(self, face_landmarks, frame_shape):
        """Dynamic camera calibration using face detection"""
        try:
            if not face_landmarks:
                return False
                
            height, width = frame_shape[:2]
            
            # Extract key facial landmarks for more accurate measurements
            # Using face mesh landmarks for precise measurements
            landmarks = face_landmarks.landmark
            
            # Get key points (left/right eye corners, nose, etc.)
            left_eye_corner = landmarks[33]   # Left eye outer corner
            right_eye_corner = landmarks[263] # Right eye outer corner
            nose_tip = landmarks[1]
            chin = landmarks[152]
            forehead = landmarks[10]
            
            # Calculate interpupillary distance in pixels
            left_eye_px = np.array([left_eye_corner.x * width, left_eye_corner.y * height])
            right_eye_px = np.array([right_eye_corner.x * width, right_eye_corner.y * height])
            interpupillary_px = np.linalg.norm(right_eye_px - left_eye_px)
            
            # Calculate face width using outer eye corners (more accurate than bounding box)
            face_width_px = interpupillary_px * 2.1  # Empirical ratio for full face width
            
            # Calculate face height
            forehead_px = np.array([forehead.x * width, forehead.y * height])
            chin_px = np.array([chin.x * width, chin.y * height])
            face_height_px = np.linalg.norm(forehead_px - chin_px)
            
            # Use interpupillary distance for most accurate scaling
            real_interpupillary = self.reference_objects['interpupillary_distance']
            pixel_ratio_from_eyes = real_interpupillary / interpupillary_px
            
            # Alternative calculation using face width
            real_face_width = self.reference_objects['average_face_width']
            pixel_ratio_from_face = real_face_width / face_width_px
            
            # Use the more conservative estimate
            pixel_ratio = min(pixel_ratio_from_eyes, pixel_ratio_from_face)
            
            # Add to history for temporal smoothing
            self.pixel_ratio_history.append(pixel_ratio)
            if len(self.pixel_ratio_history) > 10:
                self.pixel_ratio_history.pop(0)
            
            # Use median for robustness
            if len(self.pixel_ratio_history) >= 3:
                self.current_pixel_ratio = np.median(self.pixel_ratio_history)
                self.pixel_ratio_confidence = 0.9
            else:
                self.current_pixel_ratio = pixel_ratio
                self.pixel_ratio_confidence = 0.7
            
            # Update camera matrix based on measurements
            self.camera_matrix = np.array([
                [width * 0.8, 0, width / 2],
                [0, width * 0.8, height / 2],  # Assume similar focal lengths
                [0, 0, 1]
            ], dtype=np.float32)
            
            return True
            
        except Exception as e:
            print(f"Camera calibration error: {e}")
            return False
    
    def check_positioning_with_guidance(self, keypoints_2d: Dict, frame_shape: Tuple[int, int]) -> Tuple[DetectionStatus, str, Dict[str, bool], Dict]:
        """Enhanced positioning check with detailed guidance"""
        current_time = time.time()
        guidance_info = {}
        
        # Check if human is detected
        if 'holistic' not in keypoints_2d or len(keypoints_2d['holistic']) < 33:
            self.no_human_count += 1
            if self.no_human_count > 8:
                return DetectionStatus.NO_HUMAN, "Please stand in front of camera", self.body_parts_status, guidance_info
            return DetectionStatus.NO_HUMAN, "Detecting human...", self.body_parts_status, guidance_info
        
        self.no_human_count = 0
        landmarks = keypoints_2d['holistic']
        height, width = frame_shape
        
        # Enhanced body part detection
        visibility_threshold = 0.65
        
        # Reset body parts status
        body_parts = {
            'head': False,
            'shoulders': False,
            'arms': False,
            'torso': False,
            'hips': False,
            'legs': False,
            'feet': False
        }
        
        # Check each body part with specific landmark groups
        head_landmarks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        head_visible = sum(1 for i in head_landmarks if i < len(landmarks) and landmarks[i][2] > visibility_threshold)
        body_parts['head'] = head_visible >= 6
        
        shoulder_landmarks = [11, 12]
        shoulders_visible = sum(1 for i in shoulder_landmarks if landmarks[i][2] > visibility_threshold)
        body_parts['shoulders'] = shoulders_visible >= 2
        
        arm_landmarks = [13, 14, 15, 16]
        arms_visible = sum(1 for i in arm_landmarks if landmarks[i][2] > visibility_threshold)
        body_parts['arms'] = arms_visible >= 3
        
        torso_landmarks = [11, 12, 23, 24]
        torso_visible = sum(1 for i in torso_landmarks if landmarks[i][2] > visibility_threshold)
        body_parts['torso'] = torso_visible >= 4
        
        hip_landmarks = [23, 24]
        hips_visible = sum(1 for i in hip_landmarks if landmarks[i][2] > visibility_threshold)
        body_parts['hips'] = hips_visible >= 2
        
        leg_landmarks = [25, 26, 27, 28]
        legs_visible = sum(1 for i in leg_landmarks if landmarks[i][2] > visibility_threshold)
        body_parts['legs'] = legs_visible >= 3
        
        feet_landmarks = [27, 28, 29, 30, 31, 32]
        feet_visible = sum(1 for i in feet_landmarks if landmarks[i][2] > visibility_threshold)
        body_parts['feet'] = feet_visible >= 4
        
        self.body_parts_status = body_parts
        
        # Calculate positioning guidance
        if body_parts['head'] and body_parts['feet']:
            # Get head and feet positions
            head_points = [landmarks[i] for i in head_landmarks if i < len(landmarks) and landmarks[i][2] > visibility_threshold]
            feet_points = [landmarks[i] for i in feet_landmarks if landmarks[i][2] > visibility_threshold]
            
            if head_points and feet_points:
                avg_head_y = np.mean([p[1] for p in head_points])
                avg_feet_y = np.mean([p[1] for p in feet_points])
                avg_center_x = np.mean([landmarks[11][0], landmarks[12][0]]) if body_parts['shoulders'] else 0.5
                
                # Check positioning against guidance zones
                zones = self.guidance_zones
                
                # Head positioning
                head_in_zone = zones['head_zone']['y_min'] <= avg_head_y <= zones['head_zone']['y_max']
                guidance_info['head_position'] = 'good' if head_in_zone else 'adjust'
                
                # Feet positioning  
                feet_in_zone = zones['feet_zone']['y_min'] <= avg_feet_y <= zones['feet_zone']['y_max']
                guidance_info['feet_position'] = 'good' if feet_in_zone else 'adjust'
                
                # Center alignment
                center_aligned = abs(avg_center_x - 0.5) < 0.15
                guidance_info['center_alignment'] = 'good' if center_aligned else 'adjust'
                
                # Distance estimation (based on shoulder width)
                if body_parts['shoulders']:
                    shoulder_width = abs(landmarks[11][0] - landmarks[12][0])
                    if shoulder_width > 0.25:
                        guidance_info['distance'] = 'too_close'
                    elif shoulder_width < 0.12:
                        guidance_info['distance'] = 'too_far'
                    else:
                        guidance_info['distance'] = 'good'
        
        # Determine overall status
        missing_parts = [part for part, visible in body_parts.items() if not visible]
        
        if missing_parts:
            message = f"Adjust position - Missing: {', '.join(missing_parts).upper()}"
            return DetectionStatus.PARTIAL_BODY, message, body_parts, guidance_info
        
        # All parts visible - check positioning quality
        position_issues = [key for key, value in guidance_info.items() if value == 'adjust']
        
        if position_issues:
            if 'distance' in guidance_info:
                if guidance_info['distance'] == 'too_close':
                    message = "Step back - Too close to camera"
                elif guidance_info['distance'] == 'too_far':
                    message = "Step forward - Too far from camera"
                else:
                    message = "Fine-tune position - Almost perfect"
            else:
                message = "Adjust position - Center yourself"
            return DetectionStatus.PARTIAL_BODY, message, body_parts, guidance_info
        
        return DetectionStatus.GOOD_POSITION, "Perfect position - Ready to measure", body_parts, guidance_info
    
    def draw_guidance_overlay(self, frame: np.ndarray, guidance_info: Dict):
        """Draw visual guidance overlay on the frame"""
        if not self.show_guidance_overlay:
            return
        
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        # Draw guidance zones with different colors based on status
        zones = self.guidance_zones
        
        # Head zone
        head_color = (0, 255, 0) if guidance_info.get('head_position') == 'good' else (0, 255, 255)
        head_y1 = int(zones['head_zone']['y_min'] * height)
        head_y2 = int(zones['head_zone']['y_max'] * height)
        head_x1 = int((zones['head_zone']['x_center'] - zones['head_zone']['width']/2) * width)
        head_x2 = int((zones['head_zone']['x_center'] + zones['head_zone']['width']/2) * width)
        cv2.rectangle(overlay, (head_x1, head_y1), (head_x2, head_y2), head_color, 2)
        cv2.putText(overlay, "HEAD ZONE", (head_x1, head_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, head_color, 2)
        
        # Body center line
        center_color = (0, 255, 0) if guidance_info.get('center_alignment') == 'good' else (0, 255, 255)
        center_x = width // 2
        cv2.line(overlay, (center_x, 0), (center_x, height), center_color, 2, cv2.LINE_4)
        
        # Feet zone
        feet_color = (0, 255, 0) if guidance_info.get('feet_position') == 'good' else (0, 255, 255)
        feet_y1 = int(zones['feet_zone']['y_min'] * height)
        feet_y2 = int(zones['feet_zone']['y_max'] * height)
        feet_x1 = int((zones['feet_zone']['x_center'] - zones['feet_zone']['width']/2) * width)
        feet_x2 = int((zones['feet_zone']['x_center'] + zones['feet_zone']['width']/2) * width)
        cv2.rectangle(overlay, (feet_x1, feet_y1), (feet_x2, feet_y2), feet_color, 2)
        cv2.putText(overlay, "FEET ZONE", (feet_x1, feet_y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, feet_color, 2)
        
        # Optimal subject box
        opt_x1 = int(zones['optimal_subject_box']['x_min'] * width)
        opt_x2 = int(zones['optimal_subject_box']['x_max'] * width)
        opt_y1 = int(zones['optimal_subject_box']['y_min'] * height)
        opt_y2 = int(zones['optimal_subject_box']['y_max'] * height)
        
        box_color = (0, 255, 0) if all(v == 'good' for v in guidance_info.values() if v in ['good', 'adjust']) else (100, 100, 255)
        cv2.rectangle(overlay, (opt_x1, opt_y1), (opt_x2, opt_y2), box_color, 3, cv2.LINE_4)
        
        # Distance guidance
        if 'distance' in guidance_info:
            distance_status = guidance_info['distance']
            if distance_status == 'too_close':
                cv2.putText(overlay, "TOO CLOSE - STEP BACK", (width//2-150, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            elif distance_status == 'too_far':
                cv2.putText(overlay, "TOO FAR - STEP FORWARD", (width//2-150, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 3)
        
        # Grid lines for reference
        grid_color = (100, 100, 100)
        for i in range(1, 4):
            y_pos = int(height * i / 4)
            cv2.line(overlay, (0, y_pos), (width, y_pos), grid_color, 1, cv2.LINE_4)
        
        for i in range(1, 4):
            x_pos = int(width * i / 4)
            cv2.line(overlay, (x_pos, 0), (x_pos, height), grid_color, 1, cv2.LINE_4)
        
        # Apply overlay
        cv2.addWeighted(overlay, self.guidance_alpha, frame, 1 - self.guidance_alpha, 0, frame)
    
    def process_frame_enhanced(self, frame: np.ndarray) -> MeasurementResult:
        """Enhanced frame processing with improved accuracy"""
        start_time = time.time()
        
        # Detect pose keypoints
        keypoints_2d = self.detect_pose_keypoints(frame)
        
        # Enhanced positioning check with guidance
        detection_status, position_message, body_parts, guidance_info = self.check_positioning_with_guidance(
            keypoints_2d, frame.shape[:2]
        )
        
        # Draw guidance overlay
        self.draw_guidance_overlay(frame, guidance_info)
        
        # Handle detection issues
        if detection_status in [DetectionStatus.NO_HUMAN, DetectionStatus.PARTIAL_BODY]:
            if detection_status == DetectionStatus.NO_HUMAN:
                self.play_buzzer_sound()
                self.stable_measurements.clear()
                self.consecutive_stable_frames = 0
            
            processing_time = (time.time() - start_time) * 1000
            return MeasurementResult(
                height_cm=0.0,
                weight_kg=0.0,
                confidence_score=0.0,
                uncertainty_height=0.0,
                uncertainty_weight=0.0,
                processing_time_ms=processing_time,
                detection_status=detection_status,
                position_message=position_message,
                stability_frames=len(self.stable_measurements),
                is_auto_saved=False
            )
        
        # Enhanced measurement process
        try:
            # Calibrate camera using face detection
            face_detected = False
            if 'face_mesh' in keypoints_2d and keypoints_2d['face_mesh']:
                face_detected = self.calibrate_camera_with_face(keypoints_2d['face_mesh'], frame.shape)
            
            # Use default calibration if face detection fails
            if not face_detected:
                height, width = frame.shape[:2]
                self.current_pixel_ratio = 0.08  # Conservative default
                self.pixel_ratio_confidence = 0.5
                self.camera_matrix = np.array([
                    [width * 0.7, 0, width / 2],
                    [0, width * 0.7, height / 2],
                    [0, 0, 1]
                ], dtype=np.float32)
            
            # Calculate 3D keypoints
            keypoints_3d = self.calculate_3d_keypoints_enhanced(keypoints_2d, self.current_pixel_ratio)
            
            # Enhanced height estimation
            height, height_confidence = self.estimate_height_enhanced(keypoints_3d, keypoints_2d, self.current_pixel_ratio)
            
            # Enhanced weight estimation  
            anthropometric_features = self.extract_enhanced_anthropometric_features(keypoints_3d, keypoints_2d, height)
            visual_features = np.ones(2048) * 0.5  # Placeholder
            weight, weight_confidence = self.estimate_weight_enhanced(visual_features, anthropometric_features, height)
            
            # Calculate overall confidence
            overall_confidence = self.calculate_confidence_score_enhanced(
                self.pixel_ratio_confidence, 0.9, min(height_confidence, weight_confidence), height, weight
            )
            
            # Calculate uncertainties
            uncertainty_height = max(0.5, 3.0 * (1 - height_confidence))
            uncertainty_weight = max(1.0, 5.0 * (1 - weight_confidence))
            
            processing_time = (time.time() - start_time) * 1000
            
            result = MeasurementResult(
                height_cm=height,
                weight_kg=weight,
                confidence_score=overall_confidence,
                uncertainty_height=uncertainty_height,
                uncertainty_weight=uncertainty_weight,
                processing_time_ms=processing_time,
                detection_status=detection_status,
                position_message=position_message,
                stability_frames=len(self.stable_measurements),
                is_auto_saved=False
            )
            
            # Check for stability and auto-save
            if detection_status == DetectionStatus.GOOD_POSITION and overall_confidence > 0.85 and self.auto_save_enabled:
                stability_status, stability_message, stability_frames = self.check_measurement_stability(result)
                
                result.detection_status = stability_status
                result.position_message = stability_message
                result.stability_frames = stability_frames
                
                if stability_status == DetectionStatus.AUTO_SAVED:
                    # Create averaged result for saving
                    recent_measurements = self.stable_measurements[-self.stability_threshold:]
                    
                    avg_height = np.mean([m['height'] for m in recent_measurements])
                    avg_weight = np.mean([m['weight'] for m in recent_measurements])
                    avg_confidence = np.mean([m['confidence'] for m in recent_measurements])
                    
                    height_std = np.std([m['height'] for m in recent_measurements])
                    weight_std = np.std([m['weight'] for m in recent_measurements])
                    
                    final_result = MeasurementResult(
                        height_cm=avg_height,
                        weight_kg=avg_weight,
                        confidence_score=avg_confidence,
                        uncertainty_height=max(0.5, height_std),
                        uncertainty_weight=max(1.0, weight_std),
                        processing_time_ms=processing_time,
                        detection_status=DetectionStatus.AUTO_SAVED,
                        position_message="Measurement saved successfully!",
                        stability_frames=stability_frames,
                        is_auto_saved=True
                    )
                    
                    self._save_enhanced_measurement(final_result, auto_save=True)
                    self.last_auto_save = time.time()
                    
                    self.stable_measurements.clear()
                    self.consecutive_stable_frames = 0
                    
                    self.should_close_after_save = True
                    self.save_display_start = time.time()
                    
                    return final_result
            
            return result
            
        except Exception as e:
            print(f"Processing error: {e}")
            processing_time = (time.time() - start_time) * 1000
            return MeasurementResult(
                height_cm=0.0, weight_kg=0.0, confidence_score=0.0,
                uncertainty_height=0.0, uncertainty_weight=0.0,
                processing_time_ms=processing_time,
                detection_status=DetectionStatus.PARTIAL_BODY,
                position_message="Processing error - try again",
                stability_frames=0, is_auto_saved=False
            )
    
    def detect_pose_keypoints(self, frame: np.ndarray) -> Dict:
        """Enhanced pose detection with face mesh for better calibration"""
        keypoints = {}
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Holistic detection
            results = self.mp_holistic.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append([landmark.x, landmark.y, landmark.visibility])
                keypoints['holistic'] = landmarks
            
            # Face mesh for precise measurements
            face_results = self.mp_face_mesh.process(rgb_frame)
            if face_results.multi_face_landmarks:
                keypoints['face_mesh'] = face_results.multi_face_landmarks[0]
            
            # Face detection for backup reference
            face_detection_results = self.mp_face_detection.process(rgb_frame)
            if face_detection_results.detections:
                keypoints['face_detections'] = face_detection_results.detections
                
        except Exception as e:
            print(f"Pose detection error: {e}")
        
        return keypoints
    
    def calculate_3d_keypoints_enhanced(self, keypoints_2d: Dict, pixel_ratio: float) -> Optional[np.ndarray]:
        """Enhanced 3D keypoint calculation with better depth estimation"""
        try:
            if 'holistic' not in keypoints_2d:
                return None
            
            landmarks_2d = keypoints_2d['holistic']
            keypoints_3d = []
            
            for landmark in landmarks_2d:
                x_norm, y_norm, visibility = landmark
                
                if visibility < 0.6:
                    keypoints_3d.append([0, 0, 0])
                    continue
                
                # Convert to real-world coordinates using pixel ratio
                x_real = (x_norm - 0.5) * self.frame_width * pixel_ratio
                y_real = (y_norm - 0.5) * self.frame_height * pixel_ratio
                z_real = self.subject_distance_cm  # Assume subject at optimal distance
                
                keypoints_3d.append([x_real, y_real, z_real])
            
            return np.array(keypoints_3d)
            
        except Exception as e:
            print(f"3D keypoint calculation error: {e}")
            return None
    
    def estimate_height_enhanced(self, keypoints_3d: Optional[np.ndarray], 
                               keypoints_2d: Dict, pixel_ratio: float) -> Tuple[float, float]:
        """Enhanced height estimation with multiple methods"""
        try:
            if keypoints_3d is None or 'holistic' not in keypoints_2d:
                return 170.0, 0.5
            
            landmarks_2d = keypoints_2d['holistic']
            height_estimates = []
            confidences = []
            
            # Method 1: Top of head to feet (most accurate)
            head_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            foot_indices = [27, 28, 29, 30, 31, 32]
            
            visible_head = [i for i in head_indices if i < len(landmarks_2d) and landmarks_2d[i][2] > 0.7]
            visible_feet = [i for i in foot_indices if i < len(landmarks_2d) and landmarks_2d[i][2] > 0.7]
            
            if visible_head and visible_feet:
                head_y_coords = [landmarks_2d[i][1] for i in visible_head]
                feet_y_coords = [landmarks_2d[i][1] for i in visible_feet]
                
                top_head = min(head_y_coords)
                bottom_feet = max(feet_y_coords)
                
                height_pixels = (bottom_feet - top_head) * self.frame_height
                height_cm = height_pixels * pixel_ratio
                
                if 140 <= height_cm <= 220:
                    height_estimates.append(height_cm)
                    confidences.append(0.95)
            
            # Method 2: Shoulder to ankle ratio method
            if landmarks_2d[11][2] > 0.7 and landmarks_2d[12][2] > 0.7 and landmarks_2d[27][2] > 0.7:
                shoulder_center = (landmarks_2d[11][1] + landmarks_2d[12][1]) / 2
                ankle_avg = (landmarks_2d[27][1] + landmarks_2d[28][1]) / 2 if landmarks_2d[28][2] > 0.7 else landmarks_2d[27][1]
                
                shoulder_to_ankle_pixels = (ankle_avg - shoulder_center) * self.frame_height
                shoulder_to_ankle_cm = shoulder_to_ankle_pixels * pixel_ratio
                
                # Estimate total height (shoulder to ankle is approximately 75% of total height)
                estimated_height = shoulder_to_ankle_cm / 0.75
                
                if 140 <= estimated_height <= 220:
                    height_estimates.append(estimated_height)
                    confidences.append(0.85)
            
            # Method 3: Head size proportional method
            if 'face_mesh' in keypoints_2d and keypoints_2d['face_mesh']:
                try:
                    landmarks = keypoints_2d['face_mesh'].landmark
                    forehead = landmarks[10]
                    chin = landmarks[152]
                    
                    face_height_norm = abs(forehead.y - chin.y)
                    face_height_pixels = face_height_norm * self.frame_height
                    face_height_cm = face_height_pixels * pixel_ratio
                    
                    # Average face height is about 12% of total body height
                    estimated_height = face_height_cm / 0.12
                    
                    if 140 <= estimated_height <= 220:
                        height_estimates.append(estimated_height)
                        confidences.append(0.75)
                        
                except Exception:
                    pass
            
            # Ensemble method
            if height_estimates:
                # Weight by confidence
                weights = np.array(confidences)
                weights = weights / np.sum(weights)
                
                final_height = np.average(height_estimates, weights=weights)
                final_confidence = np.mean(confidences)
                
                # Add to history for temporal smoothing
                self.height_history.append(final_height)
                if len(self.height_history) > 12:
                    self.height_history.pop(0)
                
                # Apply temporal smoothing
                if len(self.height_history) >= 5:
                    # Use weighted moving average
                    recent_heights = np.array(self.height_history[-8:])
                    weights = np.exp(np.linspace(-1, 0, len(recent_heights)))  # More weight to recent
                    weights = weights / np.sum(weights)
                    
                    smoothed_height = np.average(recent_heights, weights=weights)
                    
                    # Boost confidence for consistent measurements
                    height_std = np.std(recent_heights)
                    if height_std < 1.5:
                        final_confidence = min(0.98, final_confidence * 1.3)
                    elif height_std < 3.0:
                        final_confidence = min(0.95, final_confidence * 1.15)
                    
                    return smoothed_height, final_confidence
                
                return final_height, final_confidence
            
            return 170.0, 0.4
            
        except Exception as e:
            print(f"Height estimation error: {e}")
            return 170.0, 0.3
    
    def estimate_weight_enhanced(self, visual_features: np.ndarray, 
                               anthropometric_features: np.ndarray, height: float) -> Tuple[float, float]:
        """Enhanced weight estimation using improved anthropometric formulas"""
        
        weight_estimates = []
        confidences = []
        
        try:
            # Method 1: Enhanced Body Volume Analysis
            if height > 0 and len(anthropometric_features) > 15:
                shoulder_width = anthropometric_features[10] if anthropometric_features[10] > 0 else height * 0.25
                hip_width = anthropometric_features[11] if anthropometric_features[11] > 0 else height * 0.20
                torso_length = anthropometric_features[12] if anthropometric_features[12] > 0 else height * 0.35
                
                # Improved volume calculation
                shoulder_circ = shoulder_width * 2.9
                waist_circ = hip_width * 2.2
                hip_circ = hip_width * 2.5
                
                # More accurate volume estimation
                torso_volume = (np.pi * torso_length / 3) * (
                    shoulder_circ * waist_circ / (4 * np.pi) +
                    shoulder_circ * hip_circ / (4 * np.pi) +
                    waist_circ * hip_circ / (4 * np.pi)
                ) / 100
                
                # Limb volumes with better ratios
                arm_volume = torso_volume * 0.26
                leg_volume = torso_volume * 0.32
                head_volume = torso_volume * 0.10
                
                total_volume = torso_volume + arm_volume + leg_volume + head_volume
                
                # Improved density calculation
                shoulder_hip_ratio = shoulder_width / hip_width if hip_width > 0 else 1.0
                height_factor = height / 170
                
                if shoulder_hip_ratio > 1.2:  # Athletic build
                    body_density = 1.055 + (height_factor - 1) * 0.015
                elif shoulder_hip_ratio < 0.85:  # Higher body fat
                    body_density = 0.985 + (height_factor - 1) * 0.012
                else:
                    body_density = 1.020 + (height_factor - 1) * 0.015
                
                volume_weight = total_volume * body_density
                
                # Height corrections
                if height > 185:
                    volume_weight *= 1.06
                elif height > 175:
                    volume_weight *= 1.02
                elif height < 155:
                    volume_weight *= 0.94
                elif height < 165:
                    volume_weight *= 0.97
                
                if 40 <= volume_weight <= 150:
                    weight_estimates.append(volume_weight)
                    confidences.append(0.92)
                    
        except Exception:
            pass
        
        try:
            # Method 2: Enhanced BMI-based estimation
            height_m = height / 100
            
            # Body type estimation from proportions
            shoulder_hip_ratio = anthropometric_features[8] if len(anthropometric_features) > 8 else 0.9
            
            if shoulder_hip_ratio > 1.15:  # Athletic/muscular
                target_bmi = 25.5
            elif shoulder_hip_ratio > 1.0:  # Slightly muscular
                target_bmi = 24.2
            elif shoulder_hip_ratio > 0.9:  # Average
                target_bmi = 23.0
            elif shoulder_hip_ratio > 0.8:  # Pear shape
                target_bmi = 22.2
            else:  # Apple shape
                target_bmi = 24.8
            
            # Height-based BMI adjustment
            if height > 180:
                target_bmi += 0.5
            elif height > 175:
                target_bmi += 0.2
            elif height < 160:
                target_bmi -= 0.4
            elif height < 165:
                target_bmi -= 0.2
            
            bmi_weight = target_bmi * (height_m ** 2)
            
            if 40 <= bmi_weight <= 150:
                weight_estimates.append(bmi_weight)
                confidences.append(0.88)
                
        except Exception:
            pass
        
        try:
            # Method 3: Enhanced Robinson Formula
            height_inches = height / 2.54
            
            if shoulder_hip_ratio > 1.05:  # Male-type
                robinson_weight = 52 + 1.9 * (height_inches - 60) if height_inches > 60 else 52
            else:  # Female-type
                robinson_weight = 49 + 1.7 * (height_inches - 60) if height_inches > 60 else 49
            
            # Frame size adjustment
            frame_factor = anthropometric_features[10] / height if len(anthropometric_features) > 10 else 0.23
            if frame_factor > 0.26:  # Large frame
                robinson_weight *= 1.08
            elif frame_factor < 0.20:  # Small frame
                robinson_weight *= 0.93
            
            if 40 <= robinson_weight <= 150:
                weight_estimates.append(robinson_weight)
                confidences.append(0.84)
                
        except Exception:
            pass
        
        # Fallback method
        if not weight_estimates:
            height_m = height / 100 if height > 0 else 1.7
            fallback_weight = 22.5 * (height_m ** 2)  # Average BMI
            weight_estimates.append(fallback_weight)
            confidences.append(0.6)
        
        # Ensemble with outlier removal
        if len(weight_estimates) > 2:
            median_weight = np.median(weight_estimates)
            mad = np.median(np.abs(np.array(weight_estimates) - median_weight))
            
            if mad > 0:
                z_scores = np.abs((np.array(weight_estimates) - median_weight) / (1.4826 * mad))
                valid_mask = z_scores < 2.5
                
                if np.any(valid_mask):
                    weight_estimates = [w for w, valid in zip(weight_estimates, valid_mask) if valid]
                    confidences = [c for c, valid in zip(confidences, valid_mask) if valid]
        
        # Weighted average
        weights = np.array(confidences)
        weights = weights / np.sum(weights)
        
        final_weight = np.average(weight_estimates, weights=weights)
        final_confidence = np.mean(confidences)
        
        # Temporal smoothing
        self.weight_history.append(final_weight)
        if len(self.weight_history) > 12:
            self.weight_history.pop(0)
        
        if len(self.weight_history) >= 5:
            recent_weights = np.array(self.weight_history[-8:])
            exp_weights = np.exp(np.linspace(-0.8, 0, len(recent_weights)))
            exp_weights = exp_weights / np.sum(exp_weights)
            
            smoothed_weight = np.average(recent_weights, weights=exp_weights)
            
            # Consistency bonus
            weight_std = np.std(recent_weights)
            if weight_std < 1.2:
                final_confidence = min(0.96, final_confidence * 1.25)
            elif weight_std < 2.5:
                final_confidence = min(0.92, final_confidence * 1.12)
            
            return smoothed_weight, final_confidence
        
        return max(40, min(150, final_weight)), final_confidence
    
    def extract_enhanced_anthropometric_features(self, keypoints_3d: Optional[np.ndarray], 
                                               keypoints_2d: Dict, height: float) -> np.ndarray:
        """Extract enhanced anthropometric features"""
        features = np.zeros(75)
        
        try:
            if keypoints_3d is not None and len(keypoints_3d) > 32 and 'holistic' in keypoints_2d:
                landmarks_2d = keypoints_2d['holistic']
                
                # Get key landmarks
                left_shoulder = keypoints_3d[11]
                right_shoulder = keypoints_3d[12]
                left_hip = keypoints_3d[23]
                right_hip = keypoints_3d[24]
                left_knee = keypoints_3d[25]
                right_knee = keypoints_3d[26]
                left_ankle = keypoints_3d[27]
                right_ankle = keypoints_3d[28]
                
                # Basic measurements
                shoulder_width = np.linalg.norm(left_shoulder - right_shoulder)
                hip_width = np.linalg.norm(left_hip - right_hip)
                
                shoulder_center = (left_shoulder + right_shoulder) / 2
                hip_center = (left_hip + right_hip) / 2
                knee_center = (left_knee + right_knee) / 2
                ankle_center = (left_ankle + right_ankle) / 2
                
                torso_length = np.linalg.norm(shoulder_center - hip_center)
                thigh_length = np.linalg.norm(hip_center - knee_center)
                calf_length = np.linalg.norm(knee_center - ankle_center)
                
                # Store key measurements
                features[0] = shoulder_width / height * 100 if height > 0 else 0
                features[1] = hip_width / height * 100 if height > 0 else 0
                features[2] = torso_length / height * 100 if height > 0 else 0
                features[3] = (thigh_length + calf_length) / height * 100 if height > 0 else 0
                
                # Ratios
                features[4] = shoulder_width / torso_length if torso_length > 0 else 0
                features[5] = hip_width / torso_length if torso_length > 0 else 0
                features[6] = hip_width / shoulder_width if shoulder_width > 0 else 0
                features[7] = torso_length / (thigh_length + calf_length) if (thigh_length + calf_length) > 0 else 0
                
                # Body type indicator
                features[8] = hip_width / shoulder_width if shoulder_width > 0 else 0
                
                # Absolute measurements for volume calculations
                features[10] = shoulder_width
                features[11] = hip_width
                features[12] = torso_length
                features[13] = thigh_length + calf_length
                features[14] = thigh_length
                features[15] = calf_length
                
                # Volume estimates
                features[16] = shoulder_width * hip_width * torso_length  # Torso volume
                features[17] = hip_width * 0.6 * (thigh_length + calf_length) * 2  # Leg volume
                
        except Exception as e:
            print(f"Feature extraction error: {e}")
        
        # Height-based features
        if height > 0:
            features[25] = height
            features[26] = height ** 2
            features[27] = height / 170  # Normalized
            
            # Height categories
            if height < 155:
                features[29] = 1
            elif height < 165:
                features[30] = 1
            elif height < 175:
                features[31] = 1
            elif height < 185:
                features[32] = 1
            else:
                features[33] = 1
        
        return features
    
    def calculate_confidence_score_enhanced(self, pixel_ratio_conf: float, pose_quality: float,
                                          model_agreement: float, height: float, weight: float) -> float:
        """Enhanced confidence calculation"""
        try:
            # Base confidence
            base_conf = pixel_ratio_conf * 0.4 + pose_quality * 0.3 + model_agreement * 0.3
            
            # Reasonableness checks
            height_reasonable = 1.0 if 145 <= height <= 210 else 0.6
            weight_reasonable = 1.0 if 35 <= weight <= 140 else 0.6
            
            # BMI reasonableness
            if height > 0:
                bmi = weight / ((height / 100) ** 2)
                bmi_reasonable = 1.0 if 16 <= bmi <= 40 else 0.7
            else:
                bmi_reasonable = 0.5
            
            # Combine factors
            final_conf = base_conf * height_reasonable * weight_reasonable * bmi_reasonable
            
            # Temporal consistency bonus
            if len(self.confidence_history) >= 5:
                recent_conf = self.confidence_history[-5:]
                conf_std = np.std(recent_conf)
                
                if conf_std < 0.03:
                    final_conf = min(0.97, final_conf * 1.3)
                elif conf_std < 0.06:
                    final_conf = min(0.94, final_conf * 1.15)
            
            self.confidence_history.append(final_conf)
            if len(self.confidence_history) > 10:
                self.confidence_history.pop(0)
            
            return max(0.1, min(0.98, final_conf))
            
        except Exception:
            return 0.5
    
    def check_measurement_stability(self, current_result: MeasurementResult) -> Tuple[DetectionStatus, str, int]:
        """Check measurement stability for auto-save"""
        current_time = time.time()
        
        self.stable_measurements.append({
            'height': current_result.height_cm,
            'weight': current_result.weight_kg,
            'confidence': current_result.confidence_score,
            'timestamp': current_time
        })
        
        # Keep recent measurements
        self.stable_measurements = [
            m for m in self.stable_measurements 
            if current_time - m['timestamp'] <= 4.0
        ]
        
        if len(self.stable_measurements) < self.stability_threshold:
            needed = self.stability_threshold - len(self.stable_measurements)
            return DetectionStatus.MEASURING_STABLE, f"Measuring stability... {needed} more readings needed", len(self.stable_measurements)
        
        # Check stability
        recent = self.stable_measurements[-self.stability_threshold:]
        heights = [m['height'] for m in recent]
        weights = [m['weight'] for m in recent]
        confidences = [m['confidence'] for m in recent]
        
        height_range = max(heights) - min(heights)
        weight_range = max(weights) - min(weights)
        avg_confidence = np.mean(confidences)
        
        height_stable = height_range <= self.stability_tolerance_height
        weight_stable = weight_range <= self.stability_tolerance_weight
        confidence_high = avg_confidence > 0.87
        
        if height_stable and weight_stable and confidence_high:
            self.consecutive_stable_frames += 1
            
            if self.consecutive_stable_frames >= self.stability_threshold:
                if current_time - self.last_auto_save > self.auto_save_cooldown:
                    return DetectionStatus.AUTO_SAVED, "Measurement saved - High accuracy achieved!", len(self.stable_measurements)
                else:
                    remaining = int(self.auto_save_cooldown - (current_time - self.last_auto_save))
                    return DetectionStatus.MEASURING_STABLE, f"Stable measurement (cooldown: {remaining}s)", len(self.stable_measurements)
            else:
                remaining = self.stability_threshold - self.consecutive_stable_frames
                return DetectionStatus.MEASURING_STABLE, f"Achieving stability... {remaining} more frames", len(self.stable_measurements)
        else:
            self.consecutive_stable_frames = 0
            issues = []
            if not height_stable:
                issues.append(f"Height varying by {height_range:.1f}cm")
            if not weight_stable:
                issues.append(f"Weight varying by {weight_range:.1f}kg")
            if not confidence_high:
                issues.append(f"Confidence: {avg_confidence:.1%}")
            
            return DetectionStatus.MEASURING_STABLE, f"Stabilizing: {', '.join(issues)}", len(self.stable_measurements)
    
    def _save_enhanced_measurement(self, result: MeasurementResult, auto_save: bool = False):
        """Save measurement with comprehensive data"""
        if result.height_cm > 0:
            height_m = result.height_cm / 100
            bmi = result.weight_kg / (height_m ** 2)
            
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 25:
                bmi_category = "Normal"
            elif bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"
        else:
            bmi = 0
            bmi_category = "Unknown"
        
        measurement_data = {
            'timestamp': datetime.now().isoformat(),
            'measurement_id': f"HW_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}",
            'height_cm': round(result.height_cm, 2),
            'weight_kg': round(result.weight_kg, 2),
            'bmi': round(bmi, 2),
            'bmi_category': bmi_category,
            'confidence_score': round(result.confidence_score, 4),
            'uncertainty_height_cm': round(result.uncertainty_height, 2),
            'uncertainty_weight_kg': round(result.uncertainty_weight, 2),
            'processing_time_ms': round(result.processing_time_ms, 1),
            'stability_frames': result.stability_frames,
            'auto_saved': auto_save,
            'system_version': '2.0_enhanced_with_guidance',
            'pixel_ratio_used': getattr(self, 'current_pixel_ratio', 0.08),
            'camera_calibrated': hasattr(self, 'current_pixel_ratio')
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        prefix = "AUTO_" if auto_save else "MANUAL_"
        filename = f"{prefix}measurement_{timestamp}.json"
        
        try:
            os.makedirs('measurements', exist_ok=True)
            filepath = os.path.join('measurements', filename)
            
            with open(filepath, 'w') as f:
                json.dump(measurement_data, f, indent=2)
            
            save_type = "AUTO-SAVED" if auto_save else "MANUALLY SAVED"
            print(f"\n{save_type} MEASUREMENT:")
            print(f"File: {filename}")
            print(f"Height: {result.height_cm:.1f} ± {result.uncertainty_height:.1f} cm")
            print(f"Weight: {result.weight_kg:.1f} ± {result.uncertainty_weight:.1f} kg")
            print(f"BMI: {bmi:.1f} ({bmi_category})")
            print(f"Confidence: {result.confidence_score:.1%}")
            
        except IOError as e:
            print(f"Error saving measurement: {e}")
    
    def play_buzzer_sound(self):
        """Play buzzer sound for no human detection"""
        current_time = time.time()
        if current_time - self.buzzer_cooldown > 3.0:
            try:
                winsound.Beep(600, 150)
                self.buzzer_cooldown = current_time
            except Exception:
                pass
    
    def start_enhanced_real_time_processing(self, video_source=0):
        """Start the enhanced real-time processing system"""
        cap = cv2.VideoCapture(video_source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Enhanced Height & Weight Estimation System Started")
        print("Setup Instructions:")
        print("1. Position camera at 1.2-1.5m height")
        print("2. Stand 2.5m away from camera")
        print("3. Ensure good lighting")
        print("4. Follow on-screen positioning guides")
        print("\nControls:")
        print("'q' - Quit, 's' - Manual Save, 'r' - Reset, 'g' - Toggle guidance overlay")
        print("=" * 50)
        
        cv2.namedWindow('Enhanced Height & Weight Estimation', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Enhanced Height & Weight Estimation', self.frame_width, self.frame_height)
        
        fps_counter = 0
        fps_start = time.time()
        measurements_history = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                try:
                    result = self.process_frame_enhanced(frame)
                    measurements_history.append(result)
                    
                    if len(measurements_history) > 12:
                        measurements_history.pop(0)
                    
                    self._draw_enhanced_ui(frame, result, measurements_history)
                    
                    if result.is_auto_saved:
                        self.should_close_after_save = True
                        self.save_display_start = time.time()
                    
                    if self.should_close_after_save and time.time() - self.save_display_start > 3.0:
                        print("Closing after successful measurement...")
                        break
                        
                except Exception as e:
                    print(f"Processing error: {e}")
                    cv2.putText(frame, "Processing Error", (50, 50), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # FPS monitoring
                fps_counter += 1
                if fps_counter % 30 == 0:
                    fps = 30 / (time.time() - fps_start)
                    fps_start = time.time()
                    print(f"FPS: {fps:.1f}")
                
                cv2.imshow('Enhanced Height & Weight Estimation', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and measurements_history:
                    latest = measurements_history[-1]
                    if latest.detection_status == DetectionStatus.GOOD_POSITION:
                        self._save_enhanced_measurement(latest, auto_save=False)
                    else:
                        print("Cannot save - no valid measurement")
                elif key == ord('r'):
                    self.stable_measurements.clear()
                    self.consecutive_stable_frames = 0
                    print("Stability buffer reset")
                elif key == ord('g'):
                    self.show_guidance_overlay = not self.show_guidance_overlay
                    status = "ON" if self.show_guidance_overlay else "OFF"
                    print(f"Guidance overlay: {status}")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("System closed")
    
    def _draw_position_guides(self, frame: np.ndarray):
        """Draw simple position guides and axis"""
        height, width = frame.shape[:2]
        
        # Draw center vertical and horizontal lines
        cv2.line(frame, (width//2, 0), (width//2, height), (0, 255, 0), 1)
        cv2.line(frame, (0, height//2), (width, height//2), (0, 255, 0), 1)
        
        # Draw measurement zones
        # Head zone
        head_y = int(height * 0.1)
        cv2.line(frame, (width//4, head_y), (3*width//4, head_y), (0, 255, 255), 1)
        cv2.putText(frame, "Head", (width//4 - 50, head_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Feet zone
        feet_y = int(height * 0.9)
        cv2.line(frame, (width//4, feet_y), (3*width//4, feet_y), (0, 255, 255), 1)
        cv2.putText(frame, "Feet", (width//4 - 50, feet_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Draw measurement region
        cv2.rectangle(frame, (width//4, head_y), (3*width//4, feet_y), (0, 255, 0), 1)
        
        # Add measurement scale
        scale_interval = 10  # cm
        pixel_per_cm = (feet_y - head_y) / 200  # assuming 200cm height range
        
        for i in range(0, 201, scale_interval):
            y = int(head_y + i * pixel_per_cm)
            if y < feet_y:
                cv2.line(frame, (width//4 - 5, y), (width//4, y), (0, 255, 0), 1)
                if i % 50 == 0:  # Show numbers every 50cm
                    cv2.putText(frame, f"{i}", (width//4 - 30, y), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    def _draw_enhanced_ui(self, frame: np.ndarray, result: MeasurementResult, history: List[MeasurementResult]):
        """Draw minimal UI with essential information"""
        # Draw position guides first
        self._draw_position_guides(frame)
        
        height, width = frame.shape[:2]
        if result.detection_status == DetectionStatus.NO_HUMAN:
            cv2.putText(frame, "Stand in the frame", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return
            
        # Show measurements if available
        if result.height_cm > 0 and result.weight_kg > 0:
            y_pos = 30
            cv2.putText(frame, f"H: {result.height_cm:.1f}cm", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"W: {result.weight_kg:.1f}kg", (10, y_pos + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # Calculate smoothed values
            # Show measurements with a simple display
            y_pos = height - 60
            cv2.putText(frame, f"Height: {result.height_cm:.1f}cm", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Weight: {result.weight_kg:.1f}kg", (10, y_pos + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add confidence indicator
            if result.confidence_score > 0.85:
                cv2.putText(frame, "✓", (width - 30, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

if __name__ == "__main__":
    # Create and start the enhanced height and weight estimator
    estimator = AdvancedHeightWeightEstimator(use_gpu=True)
    estimator.start_enhanced_real_time_processing()