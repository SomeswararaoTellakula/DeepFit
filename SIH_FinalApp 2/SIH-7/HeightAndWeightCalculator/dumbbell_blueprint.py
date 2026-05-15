from flask import Blueprint, render_template, Response, jsonify, request, session
import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import json
import os
import math
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from db_config import get_db
from collections import deque
from face_verifier import FaceVerifier

dumbbell_bp = Blueprint('dumbbell', __name__,
                       template_folder='templates',
                       static_folder='static',
                       url_prefix='/dumbbell')

# Global variables
camera = None
is_recording = False
session_active = False
start_time = None
face_verifier = FaceVerifier(threshold=0.70)
reference_signature = None
mismatch_count = 0
MAX_MISMATCHES = 3

# Dumbbell detection parameters
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
UP_ANGLE_THRESHOLD = 55
DOWN_ANGLE_THRESHOLD = 150
SMOOTH_WINDOW = 5
VISIBILITY_THRESHOLD = 0.5

# Exercise tracking
state = {'left': 'down', 'right': 'down'}
counts = {'left': 0, 'right': 0}
angle_buffers = {'left': deque(maxlen=SMOOTH_WINDOW), 'right': deque(maxlen=SMOOTH_WINDOW)}
estimated_weight = 0.0

exercise_stats = {
    'left_reps': 0,
    'right_reps': 0,
    'total_reps': 0,
    'left_status': 'Not visible',
    'right_status': 'Not visible',
    'estimated_weight': 0.0,
    'identity_error': False
}

def angle_between(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    v1 = (ax - bx, ay - by)
    v2 = (cx - bx, cy - by)
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 * mag2 == 0:
        return 0.0
    cosang = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cosang))

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
    global camera, is_recording, exercise_stats, state, counts, angle_buffers, estimated_weight, reference_signature
    
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    frame_count = 0
    while is_recording and camera is not None:
        success, frame = camera.read()
        if not success:
            break
        
        # Face Verification Enforcement (every 60 frames)
        if reference_signature is not None and frame_count % 60 == 0:
            current_signature = face_verifier.get_face_signature(frame)
            if current_signature is not None:
                similarity, _ = face_verifier.compute_similarity(reference_signature, current_signature)
                if similarity < face_verifier.threshold:
                    mismatch_count += 1
                    print(f"Dumbbell: Identity mismatch detected ({mismatch_count}/{MAX_MISMATCHES})")
                    cv2.putText(frame, f"IDENTITY MISMATCH ({mismatch_count})", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if mismatch_count >= MAX_MISMATCHES:
                        print("Dumbbell: Session terminated due to identity mismatch")
                        exercise_stats['identity_error'] = True
                        is_recording = False
                        break
                else:
                    mismatch_count = 0 # Reset on success
            else:
                cv2.putText(frame, "FACE NOT DETECTED", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        frame_count += 1
        
        h, w = frame.shape[:2]
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        
        left_angle_smooth = 180
        right_angle_smooth = 180
        
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            def xy(idx): return (int(lm[idx].x * w), int(lm[idx].y * h))
            
            L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
            L_ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW.value
            L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
            R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
            R_ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW.value
            R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
            
            # Left arm detection
            visible_left = (lm[L_SHOULDER].visibility > VISIBILITY_THRESHOLD and
                           lm[L_ELBOW].visibility > VISIBILITY_THRESHOLD and
                           lm[L_WRIST].visibility > VISIBILITY_THRESHOLD)
            
            if visible_left:
                left_angle = angle_between(xy(L_SHOULDER), xy(L_ELBOW), xy(L_WRIST))
                angle_buffers['left'].append(left_angle)
                if len(angle_buffers['left']) > 0:
                    left_angle_smooth = sum(angle_buffers['left']) / len(angle_buffers['left'])
                
                cur_state = state['left']
                if cur_state == 'down' and left_angle_smooth <= UP_ANGLE_THRESHOLD:
                    state['left'] = 'up'
                    counts['left'] += 1
                elif cur_state == 'up' and left_angle_smooth >= DOWN_ANGLE_THRESHOLD:
                    state['left'] = 'down'
                
                exercise_stats['left_status'] = f"L: {int(left_angle_smooth)}°"
            else:
                exercise_stats['left_status'] = "L: Not visible"
            
            # Right arm detection
            visible_right = (lm[R_SHOULDER].visibility > VISIBILITY_THRESHOLD and
                            lm[R_ELBOW].visibility > VISIBILITY_THRESHOLD and
                            lm[R_WRIST].visibility > VISIBILITY_THRESHOLD)
            
            if visible_right:
                right_angle = angle_between(xy(R_SHOULDER), xy(R_ELBOW), xy(R_WRIST))
                angle_buffers['right'].append(right_angle)
                if len(angle_buffers['right']) > 0:
                    right_angle_smooth = sum(angle_buffers['right']) / len(angle_buffers['right'])
                
                cur_state = state['right']
                if cur_state == 'down' and right_angle_smooth <= UP_ANGLE_THRESHOLD:
                    state['right'] = 'up'
                    counts['right'] += 1
                elif cur_state == 'up' and right_angle_smooth >= DOWN_ANGLE_THRESHOLD:
                    state['right'] = 'down'
                
                exercise_stats['right_status'] = f"R: {int(right_angle_smooth)}°"
            else:
                exercise_stats['right_status'] = "R: Not visible"
            
            # Update stats
            exercise_stats['left_reps'] = counts['left']
            exercise_stats['right_reps'] = counts['right']
            exercise_stats['total_reps'] = counts['left'] + counts['right']
            
            # Simple weight estimation
            total_reps = counts['left'] + counts['right']
            if total_reps > 0:
                estimated_weight = max(5.0, min(25.0, 10 + (total_reps * 0.5)))
                exercise_stats['estimated_weight'] = round(estimated_weight, 1)
            
            # Draw pose landmarks
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Draw info panel
            #cv2.rectangle(frame, (5, 5), (400, 200), (0, 0, 0), -1)
            #cv2.rectangle(frame, (5, 5), (400, 200), (0, 255, 255), 2)
            
            #cv2.putText(frame, "DUMBBELL CURL TRACKER", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            #cv2.putText(frame, f"Left Reps: {counts['left']}", (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            #cv2.putText(frame, f"Right Reps: {counts['right']}", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            #cv2.putText(frame, f"Total: {counts['left'] + counts['right']}", (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            #cv2.putText(frame, f"Weight: {estimated_weight:.1f} kg", (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            #cv2.putText(frame, exercise_stats['left_status'], (15, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            #cv2.putText(frame, exercise_stats['right_status'], (200, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@dumbbell_bp.route('/start_camera')
def start_camera():
    global camera, is_recording, session_active, start_time, state, counts, angle_buffers, estimated_weight, reference_signature, mismatch_count
    
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
                    print("✅ Face reference signature loaded for dumbbell session")

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
        
        # Reset counters
        state = {'left': 'down', 'right': 'down'}
        counts = {'left': 0, 'right': 0}
        angle_buffers = {'left': deque(maxlen=SMOOTH_WINDOW), 'right': deque(maxlen=SMOOTH_WINDOW)}
        estimated_weight = 0.0
        
        exercise_stats.update({
            'left_reps': 0,
            'right_reps': 0,
            'total_reps': 0,
            'left_status': 'Not visible',
            'right_status': 'Not visible',
            'estimated_weight': 0.0
        })
        
        return jsonify({'status': 'success', 'message': 'Started'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@dumbbell_bp.route('/stop_camera')
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
                user = get_current_user()
                duration = round(time.time() - start_time, 2) if start_time else 0
                total_reps = counts['left'] + counts['right']
                
                # Prepare MongoDB session data
                user_oid = None
                if 'user_id' in session:
                    user_oid = ObjectId(session['user_id'])
                
                if user_oid:
                    try:
                        # Create session document for analysis route
                        session_doc = {
                            "user_id": user_oid,
                            "exercise_type": "dumbbell_curls",
                            "repetitions": int(total_reps),
                            "duration": int(duration),
                            "date": datetime.utcnow()
                        }
                        session_result = db.exercise_sessions.insert_one(session_doc)
                        session_id = session_result.inserted_id
                        
                        # Create result document for analysis route
                        result_doc = {
                            "user_id": user_oid,
                            "session_id": session_id,
                            "exercise_type": "dumbbell_curls",
                            "repetitions": int(total_reps),
                            "form_score": 82,
                            "duration": int(duration),
                            "range_of_motion": 75,
                            "speed_control": 80,
                            "form_feedback": "Steady movement",
                            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                        }
                        db.exercise_results.insert_one(result_doc)
                        print(f"✅ Dumbbell session and results saved to MongoDB")
                    except Exception as e:
                        print(f"Error saving dumbbell data to standard collections: {e}")

                # Also save to existing DumbBell collection
                data = {
                    "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S'),
                    "exercise_type": "dumbbell_curls",
                    "user_email": user['email'],
                    "estimated_weight": round(estimated_weight, 2),
                    "left_reps": counts['left'],
                    "right_reps": counts['right'],
                    "total_reps": total_reps,
                    "session_duration": duration,
                    "analysis_date": datetime.now().isoformat()
                }
                db['DumbBell'].insert_one(data)
        except Exception as e:
            print(f"MongoDB save error: {e}")
        
        return jsonify({'status': 'success', 'message': 'Stopped'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@dumbbell_bp.route('/reset_counter')
def reset_counter():
    global exercise_stats, session_active, camera, is_recording, state, counts, angle_buffers, estimated_weight
    
    try:
        if is_recording:
            is_recording = False
        
        if camera is not None:
            camera.release()
            camera = None
        
        session_active = False
        
        # Reset all counters
        state = {'left': 'down', 'right': 'down'}
        counts = {'left': 0, 'right': 0}
        angle_buffers = {'left': deque(maxlen=SMOOTH_WINDOW), 'right': deque(maxlen=SMOOTH_WINDOW)}
        estimated_weight = 0.0
        
        exercise_stats.update({
            'left_reps': 0,
            'right_reps': 0,
            'total_reps': 0,
            'left_status': 'Not visible',
            'right_status': 'Not visible',
            'estimated_weight': 0.0
        })
        
        return jsonify({'status': 'success', 'message': 'Reset'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@dumbbell_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@dumbbell_bp.route('/get_stats')
def get_stats():
    return jsonify(exercise_stats)

@dumbbell_bp.route('/cleanup', methods=['POST'])
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