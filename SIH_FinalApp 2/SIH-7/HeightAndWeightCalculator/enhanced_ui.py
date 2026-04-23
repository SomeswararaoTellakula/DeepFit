import cv2
import numpy as np
from typing import Tuple, Dict, List, Optional
import math
import time

class EnhancedCameraInterface:
    """
    Enhanced camera interface with visual positioning guides and improved UX
    """
    
    def __init__(self, frame_width: int = 1280, frame_height: int = 720):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # UI Colors (BGR format for OpenCV)
        self.colors = {
            'primary': (0, 255, 0),      # Green
            'secondary': (255, 255, 0),   # Cyan
            'warning': (0, 165, 255),     # Orange
            'danger': (0, 0, 255),        # Red
            'info': (255, 255, 255),      # White
            'success': (0, 255, 0),       # Green
            'background': (40, 40, 40),   # Dark gray
            'overlay': (0, 0, 0),         # Black
        }
        
        # Animation states
        self.pulse_phase = 0
        self.scan_line_y = 0
        self.scan_direction = 1
        self.last_update = time.time()
        
        # Guide positions (normalized coordinates)
        self.guide_positions = {
            'head_zone': (0.1, 0.05, 0.9, 0.25),      # x1, y1, x2, y2
            'shoulder_zone': (0.15, 0.2, 0.85, 0.35),
            'torso_zone': (0.2, 0.3, 0.8, 0.65),
            'hip_zone': (0.25, 0.6, 0.75, 0.75),
            'leg_zone': (0.3, 0.7, 0.7, 0.95),
            'foot_zone': (0.35, 0.9, 0.65, 1.0),
        }
        
        # Optimal distance indicators
        self.distance_zones = {
            'too_close': 0.8,    # If body fills more than 80% of frame
            'optimal_min': 0.4,  # Body should fill 40-70% of frame
            'optimal_max': 0.7,
            'too_far': 0.3,      # If body fills less than 30% of frame
        }
    
    def draw_positioning_guides(self, frame: np.ndarray, detection_status: str, 
                              body_parts_status: Dict[str, bool] = None) -> np.ndarray:
        """
        Draw visual positioning guides on the frame with improved error handling and visual clarity
        
        Args:
            frame: Input frame
            detection_status: Current detection status
            body_parts_status: Status of each body part detection
            
        Returns:
            Frame with positioning guides drawn
        """
        
        try:
            # Input validation
            if frame is None or frame.size == 0:
                raise ValueError("Invalid input frame")
            
            if not isinstance(detection_status, str):
                raise ValueError("Invalid detection status type")
            
            # Ensure frame is in correct format for overlay
            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)
            
            # Create copy for overlay
            overlay = frame.copy()
            
            # Get current time for animations
            current_time = time.time()
            
            # Update animation states
            self._update_animations(current_time)
            
            # Create base overlay for all visual elements
            base_overlay = np.zeros_like(frame)
            
            # Draw elements in order of visual priority
            try:
                # 1. Draw main positioning frame
                self._draw_main_frame(base_overlay, detection_status)
                
                # 2. Draw body part zones with improved visibility
                self._draw_body_zones(base_overlay, body_parts_status or {})
                
                # 3. Draw distance indicators
                self._draw_distance_indicators(base_overlay)
                
                # 4. Draw center alignment guides
                self._draw_alignment_guides(base_overlay)
                
                # 5. Draw status-specific overlays
                if detection_status == "NO_HUMAN":
                    self._draw_no_human_overlay(base_overlay)
                elif detection_status == "PARTIAL_BODY":
                    self._draw_partial_body_overlay(base_overlay, body_parts_status or {})
                elif detection_status == "GOOD_POSITION":
                    self._draw_good_position_overlay(base_overlay)
                elif detection_status == "MEASURING_STABLE":
                    self._draw_measuring_overlay(base_overlay)
                else:
                    print(f"⚠️ Warning: Unknown detection status: {detection_status}")
                
            except Exception as e:
                print(f"⚠️ Error drawing UI element: {str(e)}")
                # Continue with partial UI if possible
            
            # Apply anti-aliasing to overlay
            base_overlay = cv2.GaussianBlur(base_overlay, (3, 3), 0)
            
            # Blend overlay with original frame using dynamic alpha
            # Adjust alpha based on lighting conditions
            frame_brightness = np.mean(frame)
            if frame_brightness < 50:  # Dark scene
                alpha = 0.4  # More visible overlay
            elif frame_brightness > 200:  # Bright scene
                alpha = 0.25  # Less visible overlay
            else:
                alpha = 0.3  # Default visibility
            
            # Ensure smooth blending
            cv2.addWeighted(base_overlay, alpha, frame, 1 - alpha, 0, frame)
            
            # Add subtle vignette effect for better focus
            height, width = frame.shape[:2]
            mask = np.zeros((height, width), dtype=np.float32)
            center = (width // 2, height // 2)
            max_rad = np.sqrt(center[0] ** 2 + center[1] ** 2)
            
            for y in range(height):
                for x in range(width):
                    distance = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
                    mask[y, x] = 1 - min(1, distance / max_rad)
            
            # Apply vignette
            mask = cv2.GaussianBlur(mask, (51, 51), 0)
            for c in range(3):
                frame[:, :, c] = frame[:, :, c] * (0.85 + 0.15 * mask)
            
            return frame
            
        except Exception as e:
            print(f"❌ Critical error in UI rendering: {str(e)}")
            # Return original frame if UI rendering fails
            return frame
        
        return frame
    
    def _update_animations(self, current_time: float):
        """Update animation states"""
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Pulse animation (for highlighting)
        self.pulse_phase += dt * 3.0  # 3 Hz pulse
        if self.pulse_phase > 2 * math.pi:
            self.pulse_phase -= 2 * math.pi
        
        # Scanning line animation
        self.scan_line_y += self.scan_direction * dt * self.frame_height * 0.5
        if self.scan_line_y >= self.frame_height:
            self.scan_line_y = self.frame_height
            self.scan_direction = -1
        elif self.scan_line_y <= 0:
            self.scan_line_y = 0
            self.scan_direction = 1
    
    def _draw_main_frame(self, overlay: np.ndarray, detection_status: str):
        """Draw the main positioning frame"""
        
        # Frame dimensions (with margins)
        margin_x = int(self.frame_width * 0.1)
        margin_y = int(self.frame_height * 0.05)
        
        frame_x1 = margin_x
        frame_y1 = margin_y
        frame_x2 = self.frame_width - margin_x
        frame_y2 = self.frame_height - margin_y
        
        # Choose color based on status
        if detection_status == "GOOD_POSITION":
            color = self.colors['success']
            thickness = 3
        elif detection_status == "MEASURING_STABLE":
            # Pulsing green for measuring
            pulse_intensity = int(128 + 127 * math.sin(self.pulse_phase))
            color = (0, pulse_intensity, 0)
            thickness = 4
        elif detection_status == "PARTIAL_BODY":
            color = self.colors['warning']
            thickness = 2
        else:
            color = self.colors['danger']
            thickness = 2
        
        # Draw main frame
        cv2.rectangle(overlay, (frame_x1, frame_y1), (frame_x2, frame_y2), color, thickness)
        
        # Draw corner markers for better visibility
        corner_size = 30
        corner_thickness = 4
        
        corners = [
            (frame_x1, frame_y1),  # Top-left
            (frame_x2, frame_y1),  # Top-right
            (frame_x1, frame_y2),  # Bottom-left
            (frame_x2, frame_y2),  # Bottom-right
        ]
        
        for i, (x, y) in enumerate(corners):
            if i == 0:  # Top-left
                cv2.line(overlay, (x, y), (x + corner_size, y), color, corner_thickness)
                cv2.line(overlay, (x, y), (x, y + corner_size), color, corner_thickness)
            elif i == 1:  # Top-right
                cv2.line(overlay, (x, y), (x - corner_size, y), color, corner_thickness)
                cv2.line(overlay, (x, y), (x, y + corner_size), color, corner_thickness)
            elif i == 2:  # Bottom-left
                cv2.line(overlay, (x, y), (x + corner_size, y), color, corner_thickness)
                cv2.line(overlay, (x, y), (x, y - corner_size), color, corner_thickness)
            elif i == 3:  # Bottom-right
                cv2.line(overlay, (x, y), (x - corner_size, y), color, corner_thickness)
                cv2.line(overlay, (x, y), (x, y - corner_size), color, corner_thickness)
    
    def _draw_body_zones(self, overlay: np.ndarray, body_parts_status: Dict[str, bool]):
        """Draw body part positioning zones"""
        
        zone_mapping = {
            'head': 'head_zone',
            'shoulders': 'shoulder_zone',
            'torso': 'torso_zone',
            'hips': 'hip_zone',
            'legs': 'leg_zone',
            'feet': 'foot_zone',
        }
        
        for body_part, zone_key in zone_mapping.items():
            if zone_key not in self.guide_positions:
                continue
            
            x1_norm, y1_norm, x2_norm, y2_norm = self.guide_positions[zone_key]
            
            x1 = int(x1_norm * self.frame_width)
            y1 = int(y1_norm * self.frame_height)
            x2 = int(x2_norm * self.frame_width)
            y2 = int(y2_norm * self.frame_height)
            
            # Choose color based on detection status
            is_detected = body_parts_status.get(body_part, False)
            
            if is_detected:
                color = self.colors['success']
                alpha_fill = 30
            else:
                color = self.colors['warning']
                alpha_fill = 50
            
            # Draw zone rectangle
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 1)
            
            # Fill zone with semi-transparent color
            zone_overlay = overlay.copy()
            cv2.rectangle(zone_overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, 1.0, zone_overlay, 0.1, 0, overlay)
            
            # Draw zone label
            label = body_part.upper()
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            label_x = x1 + (x2 - x1 - label_size[0]) // 2
            label_y = y1 + 15
            
            # Label background
            cv2.rectangle(overlay, (label_x - 2, label_y - 12), 
                         (label_x + label_size[0] + 2, label_y + 2), 
                         self.colors['background'], -1)
            
            # Label text
            cv2.putText(overlay, label, (label_x, label_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Status indicator
            status_indicator = "✓" if is_detected else "✗"
            indicator_x = x2 - 20
            indicator_y = y1 + 20
            cv2.putText(overlay, status_indicator, (indicator_x, indicator_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _draw_distance_indicators(self, overlay: np.ndarray):
        """Draw distance indicators"""
        
        # Distance scale on the right side
        scale_x = self.frame_width - 60
        scale_y1 = int(self.frame_height * 0.2)
        scale_y2 = int(self.frame_height * 0.8)
        scale_height = scale_y2 - scale_y1
        
        # Draw scale background
        cv2.rectangle(overlay, (scale_x - 10, scale_y1), (scale_x + 10, scale_y2), 
                     self.colors['background'], -1)
        
        # Draw scale markers
        markers = [
            (0.0, "TOO CLOSE", self.colors['danger']),
            (0.3, "OPTIMAL", self.colors['success']),
            (0.7, "OPTIMAL", self.colors['success']),
            (1.0, "TOO FAR", self.colors['danger']),
        ]
        
        for pos, label, color in markers:
            marker_y = scale_y1 + int(pos * scale_height)
            cv2.line(overlay, (scale_x - 15, marker_y), (scale_x + 15, marker_y), color, 2)
            
            # Label
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.3, 1)[0]
            label_x = scale_x - label_size[0] - 20
            cv2.putText(overlay, label, (label_x, marker_y + 4), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Distance instruction
        instruction = "DISTANCE"
        instruction_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        instruction_x = scale_x - instruction_size[0] // 2
        instruction_y = scale_y1 - 10
        cv2.putText(overlay, instruction, (instruction_x, instruction_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['info'], 1)
    
    def _draw_alignment_guides(self, overlay: np.ndarray):
        """Draw center alignment guides"""
        
        center_x = self.frame_width // 2
        center_y = self.frame_height // 2
        
        # Vertical center line
        cv2.line(overlay, (center_x, 0), (center_x, self.frame_height), 
                self.colors['info'], 1, cv2.LINE_AA)
        
        # Horizontal center line (for shoulder alignment)
        shoulder_y = int(self.frame_height * 0.3)
        cv2.line(overlay, (0, shoulder_y), (self.frame_width, shoulder_y), 
                self.colors['info'], 1, cv2.LINE_AA)
        
        # Center crosshair
        crosshair_size = 20
        cv2.line(overlay, (center_x - crosshair_size, center_y), 
                (center_x + crosshair_size, center_y), self.colors['info'], 2)
        cv2.line(overlay, (center_x, center_y - crosshair_size), 
                (center_x, center_y + crosshair_size), self.colors['info'], 2)
        
        # Center circle
        cv2.circle(overlay, (center_x, center_y), 5, self.colors['info'], 2)
    
    def _draw_no_human_overlay(self, overlay: np.ndarray):
        """Draw overlay for no human detected"""
        
        # Scanning line animation
        scan_y = int(self.scan_line_y)
        cv2.line(overlay, (0, scan_y), (self.frame_width, scan_y), 
                self.colors['danger'], 3)
        
        # Pulsing border
        pulse_intensity = int(100 + 100 * math.sin(self.pulse_phase))
        pulse_color = (0, 0, pulse_intensity)
        
        border_thickness = 10
        cv2.rectangle(overlay, (0, 0), (self.frame_width, self.frame_height), 
                     pulse_color, border_thickness)
        
        # Instructions
        instructions = [
            "STEP INTO THE FRAME",
            "Stand 2-3 meters from camera",
            "Ensure good lighting",
            "Face the camera directly"
        ]
        
        instruction_y = self.frame_height // 2 - 60
        for instruction in instructions:
            text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            text_x = (self.frame_width - text_size[0]) // 2
            
            # Text shadow
            cv2.putText(overlay, instruction, (text_x + 2, instruction_y + 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['overlay'], 2)
            
            # Main text
            cv2.putText(overlay, instruction, (text_x, instruction_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['danger'], 2)
            
            instruction_y += 40
    
    def _draw_partial_body_overlay(self, overlay: np.ndarray, body_parts_status: Dict[str, bool]):
        """Draw overlay for partial body detection"""
        
        # Highlight missing body parts
        missing_parts = [part for part, detected in body_parts_status.items() if not detected]
        
        if missing_parts:
            # Pulsing highlight for missing zones
            pulse_alpha = 0.3 + 0.2 * math.sin(self.pulse_phase)
            
            zone_mapping = {
                'head': 'head_zone',
                'shoulders': 'shoulder_zone',
                'torso': 'torso_zone',
                'hips': 'hip_zone',
                'legs': 'leg_zone',
                'feet': 'foot_zone',
            }
            
            for missing_part in missing_parts:
                if missing_part in zone_mapping:
                    zone_key = zone_mapping[missing_part]
                    if zone_key in self.guide_positions:
                        x1_norm, y1_norm, x2_norm, y2_norm = self.guide_positions[zone_key]
                        
                        x1 = int(x1_norm * self.frame_width)
                        y1 = int(y1_norm * self.frame_height)
                        x2 = int(x2_norm * self.frame_width)
                        y2 = int(y2_norm * self.frame_height)
                        
                        # Pulsing highlight
                        highlight_overlay = overlay.copy()
                        cv2.rectangle(highlight_overlay, (x1, y1), (x2, y2), 
                                    self.colors['warning'], -1)
                        cv2.addWeighted(overlay, 1.0, highlight_overlay, pulse_alpha, 0, overlay)
                        
                        # Missing part indicator
                        cv2.putText(overlay, "MISSING", (x1 + 10, y1 + 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['danger'], 2)
        
        # Adjustment arrows
        self._draw_adjustment_arrows(overlay, missing_parts)
    
    def _draw_adjustment_arrows(self, overlay: np.ndarray, missing_parts: List[str]):
        """Draw arrows indicating how to adjust position"""
        
        center_x = self.frame_width // 2
        center_y = self.frame_height // 2
        arrow_length = 50
        arrow_thickness = 3
        
        # Determine adjustment direction based on missing parts
        if 'head' in missing_parts:
            # Arrow pointing up (move back or up)
            cv2.arrowedLine(overlay, (center_x, center_y - 50), 
                           (center_x, center_y - 50 - arrow_length), 
                           self.colors['warning'], arrow_thickness, tipLength=0.3)
            cv2.putText(overlay, "MOVE BACK", (center_x - 50, center_y - 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['warning'], 2)
        
        if 'feet' in missing_parts:
            # Arrow pointing down (move back or down)
            cv2.arrowedLine(overlay, (center_x, center_y + 50), 
                           (center_x, center_y + 50 + arrow_length), 
                           self.colors['warning'], arrow_thickness, tipLength=0.3)
            cv2.putText(overlay, "MOVE BACK", (center_x - 50, center_y + 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['warning'], 2)
        
        if 'shoulders' in missing_parts or 'arms' in missing_parts:
            # Arrows pointing outward (face camera)
            cv2.arrowedLine(overlay, (center_x - 30, center_y), 
                           (center_x - 30 - arrow_length, center_y), 
                           self.colors['warning'], arrow_thickness, tipLength=0.3)
            cv2.arrowedLine(overlay, (center_x + 30, center_y), 
                           (center_x + 30 + arrow_length, center_y), 
                           self.colors['warning'], arrow_thickness, tipLength=0.3)
            cv2.putText(overlay, "FACE CAMERA", (center_x - 60, center_y - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['warning'], 2)
    
    def _draw_good_position_overlay(self, overlay: np.ndarray):
        """Draw overlay for good position"""
        
        # Success checkmark animation
        center_x = self.frame_width // 2
        center_y = self.frame_height // 2
        
        # Animated checkmark
        checkmark_size = 40
        checkmark_thickness = 6
        
        # Checkmark animation based on pulse phase
        animation_progress = (math.sin(self.pulse_phase) + 1) / 2  # 0 to 1
        
        if animation_progress > 0.3:
            # First line of checkmark
            line1_end_x = center_x - checkmark_size // 3
            line1_end_y = center_y + checkmark_size // 3
            cv2.line(overlay, (center_x - checkmark_size, center_y), 
                    (line1_end_x, line1_end_y), self.colors['success'], checkmark_thickness)
        
        if animation_progress > 0.6:
            # Second line of checkmark
            cv2.line(overlay, (line1_end_x, line1_end_y), 
                    (center_x + checkmark_size, center_y - checkmark_size), 
                    self.colors['success'], checkmark_thickness)
        
        # Success message
        if animation_progress > 0.8:
            cv2.putText(overlay, "PERFECT POSITION", (center_x - 100, center_y + 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['success'], 2)
    
    def _draw_measuring_overlay(self, overlay: np.ndarray):
        """Draw overlay for measuring state"""
        
        # Progress circle animation
        center_x = self.frame_width // 2
        center_y = self.frame_height // 2
        radius = 60
        
        # Rotating progress circle
        progress_angle = (self.pulse_phase / (2 * math.pi)) * 360
        
        # Background circle
        cv2.circle(overlay, (center_x, center_y), radius, self.colors['info'], 2)
        
        # Progress arc
        if progress_angle > 0:
            # OpenCV ellipse for arc drawing
            axes = (radius, radius)
            angle = 0
            start_angle = -90  # Start from top
            end_angle = start_angle + progress_angle
            
            cv2.ellipse(overlay, (center_x, center_y), axes, angle, 
                       start_angle, end_angle, self.colors['success'], 4)
        
        # Measuring text
        cv2.putText(overlay, "MEASURING...", (center_x - 70, center_y + 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['success'], 2)
        
        # Stability indicator dots
        dot_spacing = 20
        dot_radius = 5
        num_dots = 5
        
        for i in range(num_dots):
            dot_x = center_x - (num_dots - 1) * dot_spacing // 2 + i * dot_spacing
            dot_y = center_y + 130
            
            # Animate dots based on pulse phase
            dot_phase = (self.pulse_phase + i * 0.5) % (2 * math.pi)
            dot_alpha = (math.sin(dot_phase) + 1) / 2
            
            dot_color = tuple(int(c * dot_alpha) for c in self.colors['success'])
            cv2.circle(overlay, (dot_x, dot_y), dot_radius, dot_color, -1)
    
    def draw_measurement_panel(self, frame: np.ndarray, height: float, weight: float, 
                             confidence: float, uncertainty_height: float, 
                             uncertainty_weight: float, bmi: float = None) -> np.ndarray:
        """
        Draw enhanced measurement results panel
        
        Args:
            frame: Input frame
            height: Height in cm
            weight: Weight in kg
            confidence: Confidence score (0-1)
            uncertainty_height: Height uncertainty in cm
            uncertainty_weight: Weight uncertainty in kg
            bmi: BMI value (optional)
            
        Returns:
            Frame with measurement panel drawn
        """
        
        overlay = frame.copy()
        
        # Panel dimensions
        panel_width = 400
        panel_height = 220
        panel_x = 20
        panel_y = self.frame_height - panel_height - 20
        
        # Panel background with rounded corners effect
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     self.colors['background'], -1)
        
        # Panel border
        border_color = self.colors['success'] if confidence > 0.8 else self.colors['warning']
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     border_color, 2)
        
        # Title
        title_y = panel_y + 25
        cv2.putText(overlay, "MEASUREMENTS", (panel_x + 15, title_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['info'], 2)
        
        # Measurements
        text_y = title_y + 35
        line_spacing = 30
        
        # Height
        height_text = f"Height: {height:.1f} ± {uncertainty_height:.1f} cm"
        cv2.putText(overlay, height_text, (panel_x + 15, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['info'], 1)
        
        # Weight
        text_y += line_spacing
        weight_text = f"Weight: {weight:.1f} ± {uncertainty_weight:.1f} kg"
        cv2.putText(overlay, weight_text, (panel_x + 15, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['info'], 1)
        
        # BMI (if provided)
        if bmi is not None:
            text_y += line_spacing
            if bmi < 18.5:
                bmi_category = "Underweight"
                bmi_color = self.colors['warning']
            elif bmi < 25:
                bmi_category = "Normal"
                bmi_color = self.colors['success']
            elif bmi < 30:
                bmi_category = "Overweight"
                bmi_color = self.colors['warning']
            else:
                bmi_category = "Obese"
                bmi_color = self.colors['danger']
            
            bmi_text = f"BMI: {bmi:.1f} ({bmi_category})"
            cv2.putText(overlay, bmi_text, (panel_x + 15, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, bmi_color, 1)
        
        # Confidence bar
        text_y += line_spacing + 10
        cv2.putText(overlay, "Accuracy:", (panel_x + 15, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['info'], 1)
        
        # Confidence progress bar
        bar_x = panel_x + 100
        bar_y = text_y - 15
        bar_width = 200
        bar_height = 15
        
        # Background bar
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     (50, 50, 50), -1)
        
        # Progress fill
        fill_width = int(bar_width * confidence)
        fill_color = self.colors['success'] if confidence > 0.8 else self.colors['warning']
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                     fill_color, -1)
        
        # Confidence percentage
        confidence_text = f"{confidence:.1%}"
        cv2.putText(overlay, confidence_text, (bar_x + bar_width + 10, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['info'], 1)
        
        # Blend overlay with frame
        alpha = 0.9
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def draw_controls_panel(self, frame: np.ndarray) -> np.ndarray:
        """Draw controls and instructions panel"""
        
        overlay = frame.copy()
        
        # Panel dimensions
        panel_width = 300
        panel_height = 160
        panel_x = self.frame_width - panel_width - 20
        panel_y = 20
        
        # Panel background
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     self.colors['background'], -1)
        
        # Panel border
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     self.colors['info'], 1)
        
        # Title
        title_y = panel_y + 20
        cv2.putText(overlay, "CONTROLS", (panel_x + 15, title_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['info'], 2)
        
        # Controls list
        controls = [
            "'Q' - Quit",
            "'S' - Save measurement",
            "'R' - Reset stability",
            "'C' - Toggle auto-save",
            "'K' - Recalibrate camera"
        ]
        
        text_y = title_y + 25
        for control in controls:
            cv2.putText(overlay, control, (panel_x + 15, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['info'], 1)
            text_y += 20
        
        # Blend overlay with frame
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def draw_status_bar(self, frame: np.ndarray, status_message: str, 
                       calibration_status: str = None, fps: float = None) -> np.ndarray:
        """Draw status bar at the top of the frame"""
        
        overlay = frame.copy()
        
        # Status bar dimensions
        bar_height = 40
        bar_y = 0
        
        # Status bar background
        cv2.rectangle(overlay, (0, bar_y), (self.frame_width, bar_y + bar_height), 
                     self.colors['background'], -1)
        
        # Status message
        cv2.putText(overlay, status_message, (20, bar_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['info'], 2)
        
        # Calibration status (if provided)
        if calibration_status:
            calib_text_size = cv2.getTextSize(calibration_status, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            calib_x = self.frame_width - calib_text_size[0] - 150
            cv2.putText(overlay, calibration_status, (calib_x, bar_y + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['secondary'], 1)
        
        # FPS counter (if provided)
        if fps is not None:
            fps_text = f"FPS: {fps:.1f}"
            fps_text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            fps_x = self.frame_width - fps_text_size[0] - 20
            cv2.putText(overlay, fps_text, (fps_x, bar_y + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['info'], 1)
        
        # Blend overlay with frame
        alpha = 0.9
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def create_calibration_interface(self, frame: np.ndarray, 
                                   chessboard_detected: bool = False,
                                   captured_images: int = 0,
                                   required_images: int = 15) -> np.ndarray:
        """Create calibration interface overlay"""
        
        overlay = frame.copy()
        
        # Calibration instructions panel
        panel_width = 500
        panel_height = 200
        panel_x = (self.frame_width - panel_width) // 2
        panel_y = 50
        
        # Panel background
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     self.colors['background'], -1)
        
        # Panel border
        border_color = self.colors['success'] if chessboard_detected else self.colors['warning']
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     border_color, 3)
        
        # Title
        title_y = panel_y + 30
        cv2.putText(overlay, "CAMERA CALIBRATION", (panel_x + 120, title_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['info'], 2)
        
        # Instructions
        instructions = [
            "1. Hold chessboard pattern in view",
            "2. Move to different positions and angles",
            "3. Press SPACE when pattern is detected",
            "4. Press ESC when finished"
        ]
        
        text_y = title_y + 40
        for instruction in instructions:
            cv2.putText(overlay, instruction, (panel_x + 20, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['info'], 1)
            text_y += 25
        
        # Progress
        progress_text = f"Images captured: {captured_images}/{required_images}"
        cv2.putText(overlay, progress_text, (panel_x + 20, text_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['secondary'], 2)
        
        # Progress bar
        progress_bar_x = panel_x + 20
        progress_bar_y = text_y + 40
        progress_bar_width = panel_width - 40
        progress_bar_height = 15
        
        # Background
        cv2.rectangle(overlay, (progress_bar_x, progress_bar_y), 
                     (progress_bar_x + progress_bar_width, progress_bar_y + progress_bar_height), 
                     (50, 50, 50), -1)
        
        # Progress fill
        progress = captured_images / required_images
        fill_width = int(progress_bar_width * progress)
        cv2.rectangle(overlay, (progress_bar_x, progress_bar_y), 
                     (progress_bar_x + fill_width, progress_bar_y + progress_bar_height), 
                     self.colors['success'], -1)
        
        # Detection status
        if chessboard_detected:
            status_text = "CHESSBOARD DETECTED - Press SPACE to capture"
            status_color = self.colors['success']
        else:
            status_text = "Position chessboard pattern in view"
            status_color = self.colors['warning']
        
        status_y = self.frame_height - 50
        text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        status_x = (self.frame_width - text_size[0]) // 2
        
        # Status background
        cv2.rectangle(overlay, (status_x - 10, status_y - 25), 
                     (status_x + text_size[0] + 10, status_y + 5), 
                     self.colors['background'], -1)
        
        cv2.putText(overlay, status_text, (status_x, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Blend overlay with frame
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame


# Example usage and integration
def demo_enhanced_interface():
    """Demo function to show the enhanced interface"""
    
    # Initialize interface
    interface = EnhancedCameraInterface(1280, 720)
    
    # Create a demo frame
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Simulate different states
    states = [
        ("NO_HUMAN", {}),
        ("PARTIAL_BODY", {"head": True, "shoulders": True, "torso": False, "hips": False, "legs": False, "feet": False}),
        ("GOOD_POSITION", {"head": True, "shoulders": True, "torso": True, "hips": True, "legs": True, "feet": True}),
        ("MEASURING_STABLE", {"head": True, "shoulders": True, "torso": True, "hips": True, "legs": True, "feet": True}),
    ]
    
    for detection_status, body_parts in states:
        demo_frame = frame.copy()
        
        # Draw positioning guides
        demo_frame = interface.draw_positioning_guides(demo_frame, detection_status, body_parts)
        
        # Draw measurement panel (for good position states)
        if detection_status in ["GOOD_POSITION", "MEASURING_STABLE"]:
            demo_frame = interface.draw_measurement_panel(
                demo_frame, 175.5, 68.2, 0.92, 1.2, 2.1, 22.3
            )
        
        # Draw controls panel
        demo_frame = interface.draw_controls_panel(demo_frame)
        
        # Draw status bar
        status_messages = {
            "NO_HUMAN": "No human detected - Please step into frame",
            "PARTIAL_BODY": "Adjust position - Some body parts missing",
            "GOOD_POSITION": "Perfect position - Ready for measurement",
            "MEASURING_STABLE": "Measuring - Hold steady for accurate results"
        }
        
        demo_frame = interface.draw_status_bar(
            demo_frame, 
            status_messages[detection_status],
            "Calibrated (0.45px)",
            30.0
        )
        
        # Save demo frame
        cv2.imwrite(f"demo_{detection_status.lower()}.png", demo_frame)
        print(f"Saved demo_{detection_status.lower()}.png")


if __name__ == "__main__":
    demo_enhanced_interface()

