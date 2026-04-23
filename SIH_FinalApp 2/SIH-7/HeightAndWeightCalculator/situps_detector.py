import cv2
import mediapipe as mp
import numpy as np
import math

class SitupsDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Situps specific variables
        self.count = 0
        self.stage = None  # "down" or "up"
        self.form_feedback = "Get Ready"
        self.last_angle = 0
        
        # Angle thresholds for situps
        self.down_threshold = 160  # Lying down
        self.up_threshold = 90     # Sitting up
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b) 
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def get_form_percentage(self, angle):
        """Calculate form percentage based on angle and movement quality"""
        if angle >= self.down_threshold:
            return 0  # Starting position
        elif angle <= self.up_threshold:
            return 100  # Full situp
        else:
            # Linear interpolation between thresholds with quality bonus
            base_percentage = int(np.interp(angle, [self.up_threshold, self.down_threshold], [100, 0]))
            # Add quality bonus based on rep count (consistency)
            quality_bonus = min(15, self.count * 2)
            return min(100, base_percentage + quality_bonus)
    
    def detect_situps(self, frame):
        """Main detection function"""
        # Convert BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            try:
                # Get key points for situps detection
                # We'll use shoulder, hip, and knee to measure torso angle
                left_shoulder = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                ]
                left_hip = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
                ]
                left_knee = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y
                ]
                
                # Calculate the torso angle (shoulder-hip-knee)
                torso_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
                self.last_angle = torso_angle
                
                # Improved situps counting logic with better thresholds
                if torso_angle > 150:  # Lying down position (more lenient)
                    if self.stage != "down":
                        self.stage = "down"
                        self.form_feedback = "Go Up!"
                        
                elif torso_angle < 100 and self.stage == "down":  # Sitting up position
                    self.stage = "up"
                    self.count += 1
                    self.form_feedback = f"Rep {self.count}! Great form!"
                    
                else:
                    # In between positions with better guidance
                    if self.stage == "down" and 100 <= torso_angle <= 150:
                        self.form_feedback = "Keep Going Up!"
                    elif self.stage == "up" and 100 <= torso_angle <= 150:
                        self.form_feedback = "Go Down Slowly"
                    elif torso_angle > 150:
                        self.form_feedback = "Ready Position"
                    else:
                        self.form_feedback = "Get in Position"
                
                # Draw pose landmarks
                self.mp_draw.draw_landmarks(
                    frame, 
                    results.pose_landmarks, 
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                )
                
                # Draw angle visualization
                h, w, _ = frame.shape
                shoulder_px = (int(left_shoulder[0] * w), int(left_shoulder[1] * h))
                hip_px = (int(left_hip[0] * w), int(left_hip[1] * h))
                knee_px = (int(left_knee[0] * w), int(left_knee[1] * h))
                
                # Draw lines
                cv2.line(frame, shoulder_px, hip_px, (255, 255, 255), 3)
                cv2.line(frame, hip_px, knee_px, (255, 255, 255), 3)
                
                # Draw circles at joints
                cv2.circle(frame, shoulder_px, 8, (0, 255, 0), cv2.FILLED)
                cv2.circle(frame, hip_px, 8, (0, 255, 0), cv2.FILLED)
                cv2.circle(frame, knee_px, 8, (0, 255, 0), cv2.FILLED)
                
                # Display angle
                cv2.putText(frame, f'Angle: {int(torso_angle)}°', 
                           (hip_px[0] - 50, hip_px[1] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            except Exception as e:
                self.form_feedback = "Position yourself properly"
                print(f"Detection error: {e}")
        else:
            self.form_feedback = "No pose detected"
        
        # Draw stats on frame
        cv2.putText(frame, f'Situps: {self.count}', 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, self.form_feedback, 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return frame
    
    def get_stats(self):
        """Return current statistics with improved form calculation"""
        # Calculate form percentage based on reps and consistency
        if self.count == 0:
            form_percentage = 0
        else:
            # Base form percentage on rep count and angle quality
            base_form = min(95, max(60, 70 + (self.count * 3)))
            angle_quality = self.get_form_percentage(self.last_angle) if self.last_angle else 0
            form_percentage = int((base_form + angle_quality) / 2)
        
        return {
            'reps': self.count,
            'feedback': self.form_feedback,
            'form_percentage': form_percentage,
            'angle': int(self.last_angle) if self.last_angle else 0
        }
    
    def reset(self):
        """Reset counter and state"""
        self.count = 0
        self.stage = None
        self.form_feedback = "Get Ready"
        self.last_angle = 0