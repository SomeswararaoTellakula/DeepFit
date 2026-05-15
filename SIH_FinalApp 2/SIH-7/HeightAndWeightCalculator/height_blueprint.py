from flask import Blueprint, render_template, Response, jsonify, request, session, current_app
from error_logger import log_error, log_warning, log_info
from session_manager import login_required, get_current_user
from db_config import get_db
import cv2
import numpy as np
import threading
import time
import json
import os
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from integrated_system import IntegratedHeightWeightSystem, DetectionStatus, MeasurementResult
from face_verifier import FaceVerifier

# Create blueprint
height_bp = Blueprint('height', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/height')

# Global variables for video processing
camera = None
is_recording = False
session_active = False
system = None
face_verifier = FaceVerifier(threshold=0.70)
reference_signature = None
mismatch_count = 0
MAX_MISMATCHES = 3
identity_error = False

def get_system():
    global system
    if system is None:
        system = IntegratedHeightWeightSystem(use_gpu=True)
    return system

def generate_frames():
    """Generate video frames for streaming with integrated Height/Weight logic and Face Verification"""
    global camera, is_recording, system, reference_signature, mismatch_count, identity_error
    
    sys = get_system()
    measurements_history = []
    frame_count = 0
    
    while is_recording and camera is not None:
        success, frame = camera.read()
        if not success:
            break
        
        # Periodically run Face Verification Enforcement (every 30 frames)
        if reference_signature is not None and frame_count % 30 == 0:
            current_signature = face_verifier.get_face_signature(frame)
            if current_signature is not None:
                similarity, _ = face_verifier.compute_similarity(reference_signature, current_signature)
                is_match = similarity >= face_verifier.threshold
                if not is_match:
                    mismatch_count += 1
                    log_warning(f"Height: Identity mismatch detected ({mismatch_count}/{MAX_MISMATCHES}): {similarity:.4f}")
                    cv2.putText(frame, f"IDENTITY MISMATCH ({mismatch_count})", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if mismatch_count >= MAX_MISMATCHES:
                        log_error("Height: Session terminated due to identity mismatch")
                        identity_error = True
                        is_recording = False
                        break
                else:
                    mismatch_count = 0 # Reset on success
            else:
                cv2.putText(frame, "FACE NOT DETECTED", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        frame_count += 1
        
        # Process frame using the integrated system logic
        try:
            result = sys.process_frame_integrated(frame)
            measurements_history.append(result)
            
            if len(measurements_history) > 10:
                measurements_history.pop(0)
            
            # Update FPS (internal tracking)
            sys.fps_counter += 1
            if sys.fps_counter % 30 == 0:
                fps_end_time = time.time()
                sys.current_fps = 30 / (fps_end_time - sys.fps_start_time)
                sys.fps_start_time = fps_end_time
            
            # Draw the integrated UI on the frame
            sys._draw_integrated_ui(frame, result, measurements_history)
            
        except Exception as e:
            log_error(f"Processing error in height video feed: {e}")
            cv2.putText(frame, "Processing Error", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Encode frame for MJPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@height_bp.route('/')
def index():
    """Main page for Height & Weight estimation"""
    return render_template('height.html')

@height_bp.route('/start_camera', methods=['POST'])
def start_camera():
    """Start camera and initialize system"""
    global camera, is_recording, session_active, reference_signature, mismatch_count, identity_error
    
    try:
        # Get user for face verification reference
        db = get_db()
        user_id = session.get('user_id')
        if user_id and db is not None:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if user and 'photo' in user:
                ref_img = face_verifier.decode_base64_image(user['photo'])
                if ref_img is not None:
                    reference_signature = face_verifier.get_face_signature(ref_img)
                    log_info("Face reference signature loaded for session")

        # Always release existing camera first
        if camera is not None:
            camera.release()
            camera = None
        
        # Initialize camera
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'status': 'error', 'message': 'Camera unavailable'})
        
        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        is_recording = True
        session_active = True
        mismatch_count = 0
        identity_error = False
        
        # Reset system state
        sys = get_system()
        sys.measurement_history = []
        sys.stability_buffer = []
        sys.consecutive_stable_frames = 0
        
        return jsonify({'status': 'success', 'message': 'Started'})
        
    except Exception as e:
        log_error(f"Error starting height camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@height_bp.route('/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera and cleanup"""
    global camera, is_recording, session_active
    
    try:
        is_recording = False
        session_active = False
        
        if camera:
            camera.release()
            camera = None
        
        return jsonify({'status': 'success', 'message': 'Stopped'})
    except Exception as e:
        log_error(f"Error stopping height camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@height_bp.route('/video_feed')
def video_feed():
    """Video stream endpoint"""
    log_info("Video feed request received")
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame',
                   headers={
                       'Cache-Control': 'no-cache, no-store, must-revalidate',
                       'Pragma': 'no-cache',
                       'Expires': '0'
                   })

@height_bp.route('/get_stats')
def get_stats():
    """Get current measurement stats"""
    sys = get_system()
    
    # Get latest result if available
    latest_result = None
    if sys.measurement_history:
        latest_result = sys.measurement_history[-1]
    
    stats = {
        'height': round(latest_result.height_cm, 1) if latest_result else 0,
        'weight': round(latest_result.weight_kg, 1) if latest_result else 0,
        'confidence': round(latest_result.confidence_score * 100, 1) if latest_result else 0,
        'status': latest_result.detection_status.value if latest_result else "Initializing",
        'message': latest_result.position_message if latest_result else "Connecting...",
        'is_stable': latest_result.detection_status == DetectionStatus.MEASURING_STABLE if latest_result else False,
        'is_auto_saved': latest_result.is_auto_saved if latest_result else False,
        'identity_error': identity_error
    }
    
    return jsonify(stats)
