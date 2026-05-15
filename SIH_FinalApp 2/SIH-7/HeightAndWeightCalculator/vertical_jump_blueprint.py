from flask import Blueprint, render_template, Response, jsonify, request, session
import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import json
import os
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from db_config import get_db
from advanced_jump_detector import AdvancedJumpDetector
from face_verifier import FaceVerifier

vertical_jump_bp = Blueprint('vertical_jump', __name__,
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/vertical_jump')

# Global variables
camera = None
is_recording = False
session_active = False
start_time = None
jump_detector = AdvancedJumpDetector()
face_verifier = FaceVerifier(threshold=0.70)
reference_signature = None
mismatch_count = 0
MAX_MISMATCHES = 3
exercise_stats = {
    'total_jumps': 0,
    'current_height': 0.0,
    'max_height': 0.0,
    'state': 'GROUND',
    'calibrated': False,
    'feedback': 'System Ready',
    'identity_error': False
}

def get_current_user():
    try:
        db = get_db()
        if db and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                return {'email': user.get('email', 'user@example.com')}
        return {'email': 'test_user_001@example.com'}
    except:
        return {'email': 'test_user_001@example.com'}

def generate_frames():
    global camera, is_recording, exercise_stats, reference_signature, mismatch_count
    
    frame_count = 0
    while is_recording and camera is not None:
        success, frame = camera.read()
        if not success:
            break
        
        # Face Verification Enforcement (every 60 frames)
        if reference_signature is not None and frame_count % 60 == 0:
            current_signature = face_verifier.get_face_signature(frame)
            if current_signature is not None:
                similarity = face_verifier.calculate_similarity(reference_signature, current_signature)
                if similarity < face_verifier.threshold:
                    mismatch_count += 1
                    print(f"Jump: Identity mismatch detected ({mismatch_count}/{MAX_MISMATCHES})")
                    cv2.putText(frame, f"IDENTITY MISMATCH ({mismatch_count})", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if mismatch_count >= MAX_MISMATCHES:
                        print("Jump: Session terminated due to identity mismatch")
                        exercise_stats['identity_error'] = True
                        is_recording = False
                        break
                else:
                    mismatch_count = 0 # Reset on success
            else:
                cv2.putText(frame, "FACE NOT DETECTED", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        frame_count += 1
        
        # Process frame
        frame = jump_detector.process_frame(frame)
        
        # Update stats
        stats = jump_detector.get_performance_stats()
        exercise_stats.update({
            'total_jumps': stats['total_jumps'],
            'current_height': stats['current_height'],
            'max_height': stats['max_height'],
            'state': stats['state'],
            'calibrated': stats['calibrated'],
            'feedback': stats['feedback']
        })
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@vertical_jump_bp.route('/start_camera')
def start_camera():
    global camera, is_recording, session_active, start_time, reference_signature, mismatch_count
    
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
                    print("✅ Face reference signature loaded for jump session")

        if camera is not None:
            camera.release()
            camera = None
        
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'status': 'error', 'message': 'Camera unavailable'})
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        is_recording = True
        session_active = True
        start_time = time.time()
        mismatch_count = 0
        exercise_stats['identity_error'] = False
        
        jump_detector.reset_session()
        
        return jsonify({'status': 'success', 'message': 'Started'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@vertical_jump_bp.route('/stop_camera')
def stop_camera():
    global camera, is_recording, session_active
    
    try:
        is_recording = False
        session_active = False
        
        if camera:
            camera.release()
            camera = None
        
        # Save to MongoDB
        try:
            db = get_db()
            if db:
                stats = jump_detector.get_performance_stats()
                duration = round(time.time() - start_time, 2) if start_time else 0
                
                # Prepare MongoDB session data
                user_oid = None
                if 'user_id' in session:
                    user_oid = ObjectId(session['user_id'])
                
                if user_oid:
                    try:
                        # Create session document for analysis route
                        session_doc = {
                            "user_id": user_oid,
                            "exercise_type": "vertical_jump",
                            "repetitions": int(stats['total_jumps']),
                            "duration": int(duration),
                            "date": datetime.utcnow()
                        }
                        session_result = db.exercise_sessions.insert_one(session_doc)
                        session_id = session_result.inserted_id
                        
                        # Create result document for analysis route
                        result_doc = {
                            "user_id": user_oid,
                            "session_id": session_id,
                            "exercise_type": "vertical_jump",
                            "repetitions": int(stats['total_jumps']),
                            "form_score": 88,
                            "duration": int(duration),
                            "range_of_motion": 85,
                            "speed_control": 90,
                            "form_feedback": f"Max height: {stats['max_height']:.1f}cm",
                            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                        }
                        db.exercise_results.insert_one(result_doc)
                        print(f"✅ Vertical jump session and results saved to MongoDB")
                    except Exception as e:
                        print(f"Error saving vertical jump data to standard collections: {e}")
        except Exception as e:
            print(f"Error in vertical jump stop_camera: {e}")

        # Save to existing Vertical_Jump collection via detector
        jump_detector.save_to_mongodb()
        
        return jsonify({'status': 'success', 'message': 'Stopped'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@vertical_jump_bp.route('/reset_counter')
def reset_counter():
    global exercise_stats, session_active, camera, is_recording
    
    try:
        if is_recording:
            is_recording = False
        
        if camera is not None:
            camera.release()
            camera = None
        
        session_active = False
        jump_detector.reset_session()
        
        exercise_stats.update({
            'total_jumps': 0,
            'current_height': 0.0,
            'max_height': 0.0,
            'state': 'GROUND',
            'calibrated': False,
            'feedback': 'System Ready'
        })
        
        return jsonify({'status': 'success', 'message': 'Reset'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@vertical_jump_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@vertical_jump_bp.route('/get_stats')
def get_stats():
    if is_recording:
        stats = jump_detector.get_performance_stats()
        exercise_stats.update({
            'total_jumps': stats['total_jumps'],
            'current_height': stats['current_height'],
            'max_height': stats['max_height'],
            'state': stats['state'],
            'calibrated': stats['calibrated'],
            'feedback': stats['feedback']
        })
    
    return jsonify(exercise_stats)

@vertical_jump_bp.route('/cleanup', methods=['POST'])
def cleanup():
    global camera, is_recording, session_active
    
    try:
        is_recording = False
        session_active = False
        
        if camera is not None:
            camera.release()
            camera = None
        
        return '', 204
    except Exception:
        return '', 204