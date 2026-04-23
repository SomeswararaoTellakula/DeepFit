import cv2
import mediapipe as mp
import math
import time
from collections import deque
import joblib
import numpy as np
import os
import sys
from datetime import datetime
from pymongo import MongoClient

# ============ HELPER FUNCTIONS ============
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

def detect_cheating(estimated_weight, rom_list, tempo_list):
    warnings = []
    if not rom_list or not tempo_list:
        warnings.append("No reps detected")
        return warnings
    avg_rom = sum(rom_list) / len(rom_list)
    avg_tempo = sum(tempo_list) / len(tempo_list)
    if avg_rom < 70:
        warnings.append("ROM too short — partial curls")
    if estimated_weight >= 15 and avg_tempo < 1.0:
        warnings.append("Unrealistic speed for heavy dumbbell")
    if len(tempo_list) > 2 and (max(tempo_list) - min(tempo_list) < 0.2 and estimated_weight >= 10):
        warnings.append("No fatigue variation — possible wrong weight")
    return warnings

# Load model and scaler with error handling
try:
    if os.path.exists('weight_model.pkl'):
        model = joblib.load('weight_model.pkl')
        scaler = joblib.load('scaler.pkl')
    elif os.path.exists('models/weight_rf_model.pkl'):
        model = joblib.load('models/weight_rf_model.pkl')
        scaler = joblib.load('models/weight_scaler.pkl')
    else:
        print("Warning: Model files not found. Using default weight estimation.")
        model = None
        scaler = None
except Exception as e:
    print(f"Warning: Could not load model files: {e}. Using default weight estimation.")
    model = None
    scaler = None

# ============ MAIN PROGRAM ============
print("\n=== Exercise Guidelines ===")
print("- Keep elbows fixed close to your body")
print("- Full range of motion: start with arms straight, curl up to shoulders")
print("- Controlled tempo: 1-2 seconds up, 2-3 seconds down")
print("- Face the camera directly for accurate detection")
print("- Exercise will run for 3 minutes or until 'q' is pressed")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
UP_ANGLE_THRESHOLD = 55
DOWN_ANGLE_THRESHOLD = 150
SMOOTH_WINDOW = 5
VISIBILITY_THRESHOLD = 0.5

# Initialize camera with error handling
print("Initializing camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera. Please check if camera is connected and not in use.")
    sys.exit(1)

# Set camera properties for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Camera initialized successfully!")
print("Starting dumbbell curl detection...")
start_time = time.time()

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    state = {'left': 'down', 'right': 'down'}
    counts = {'left': 0, 'right': 0}
    angle_buffers = {'left': deque(maxlen=SMOOTH_WINDOW), 'right': deque(maxlen=SMOOTH_WINDOW)}
    last_up_time = {'left': None, 'right': None}
    last_down_time = {'left': None, 'right': None}
    tempos = {'left': [], 'right': []}
    roms = {'left': [], 'right': []}
    rep_min_angle = {'left': 180, 'right': 180}
    rep_max_angle = {'left': 0, 'right': 0}
    estimated_weight = 0.0

    while True:
        elapsed = time.time() - start_time
        if elapsed > 180:
            break

        ret, frame = cap.read()
        if not ret:
            break
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

            visible_left = (lm[L_SHOULDER].visibility > VISIBILITY_THRESHOLD and
                            lm[L_ELBOW].visibility > VISIBILITY_THRESHOLD and
                            lm[L_WRIST].visibility > VISIBILITY_THRESHOLD)
            # Only process left arm if right arm is NOT moving (right arm must be in 'down' state and not flexed)
            right_static = True
            if lm[R_SHOULDER].visibility > VISIBILITY_THRESHOLD and lm[R_ELBOW].visibility > VISIBILITY_THRESHOLD and lm[R_WRIST].visibility > VISIBILITY_THRESHOLD:
                right_angle = angle_between(xy(R_SHOULDER), xy(R_ELBOW), xy(R_WRIST))
                if right_angle < DOWN_ANGLE_THRESHOLD - 20:  # right arm is flexed or moving
                    right_static = False
            if visible_left and right_static:
                left_angle = angle_between(xy(L_SHOULDER), xy(L_ELBOW), xy(L_WRIST))
                angle_buffers['left'].append(left_angle)
                if len(angle_buffers['left']) > 0:
                    left_angle_smooth = sum(angle_buffers['left']) / len(angle_buffers['left'])
                rep_min_angle['left'] = min(rep_min_angle['left'], left_angle_smooth)
                rep_max_angle['left'] = max(rep_max_angle['left'], left_angle_smooth)
                cur_state = state['left']
                now = time.time()
                # Require a minimum ROM for a valid rep
                min_required_rom = 30
                if cur_state == 'down' and left_angle_smooth <= UP_ANGLE_THRESHOLD:
                    if (rep_max_angle['left'] - rep_min_angle['left']) >= min_required_rom:
                        state['left'] = 'up'
                        if last_down_time['left'] is not None:
                            concentric_time = now - last_down_time['left']
                            tempos['left'].append(concentric_time)
                            roms['left'].append(rep_max_angle['left'] - rep_min_angle['left'])
                        last_up_time['left'] = now
                        counts['left'] += 1
                        rep_min_angle['left'] = 180
                        rep_max_angle['left'] = 0
                elif cur_state == 'up' and left_angle_smooth >= DOWN_ANGLE_THRESHOLD:
                    state['left'] = 'down'
                    last_down_time['left'] = now

            visible_right = (lm[R_SHOULDER].visibility > VISIBILITY_THRESHOLD and
                             lm[R_ELBOW].visibility > VISIBILITY_THRESHOLD and
                             lm[R_WRIST].visibility > VISIBILITY_THRESHOLD)
            # Only process right arm if left arm is NOT moving (left arm must be in 'down' state and not flexed)
            left_static = True
            if lm[L_SHOULDER].visibility > VISIBILITY_THRESHOLD and lm[L_ELBOW].visibility > VISIBILITY_THRESHOLD and lm[L_WRIST].visibility > VISIBILITY_THRESHOLD:
                left_angle = angle_between(xy(L_SHOULDER), xy(L_ELBOW), xy(L_WRIST))
                if left_angle < DOWN_ANGLE_THRESHOLD - 20:  # left arm is flexed or moving
                    left_static = False
            if visible_right and left_static:
                right_angle = angle_between(xy(R_SHOULDER), xy(R_ELBOW), xy(R_WRIST))
                angle_buffers['right'].append(right_angle)
                if len(angle_buffers['right']) > 0:
                    right_angle_smooth = sum(angle_buffers['right']) / len(angle_buffers['right'])
                rep_min_angle['right'] = min(rep_min_angle['right'], right_angle_smooth)
                rep_max_angle['right'] = max(rep_max_angle['right'], right_angle_smooth)
                cur_state = state['right']
                now = time.time()
                min_required_rom = 30
                if cur_state == 'down' and right_angle_smooth <= UP_ANGLE_THRESHOLD:
                    if (rep_max_angle['right'] - rep_min_angle['right']) >= min_required_rom:
                        state['right'] = 'up'
                        if last_down_time['right'] is not None:
                            concentric_time = now - last_down_time['right']
                            tempos['right'].append(concentric_time)
                            roms['right'].append(rep_max_angle['right'] - rep_min_angle['right'])
                        last_up_time['right'] = now
                        counts['right'] += 1
                        rep_min_angle['right'] = 180
                        rep_max_angle['right'] = 0
                elif cur_state == 'up' and right_angle_smooth >= DOWN_ANGLE_THRESHOLD:
                    state['right'] = 'down'
                    last_down_time['right'] = now

            # --- Use model for weight prediction ---
            # Use average ROM and average tempo as features
            all_roms = roms['left'] + roms['right']
            all_tempos = tempos['left'] + tempos['right']
            if len(all_roms) > 0 and len(all_tempos) > 0:
                avg_rom = sum(all_roms) / len(all_roms)
                avg_velocity = 1.0 / (sum(all_tempos) / len(all_tempos)) if sum(all_tempos) > 0 else 0.1
                
                if model is not None and scaler is not None:
                    try:
                        # Try using pandas first
                        try:
                            import pandas as pd
                            X_pred = pd.DataFrame([[avg_rom, avg_velocity, 0]], columns=['avg_rom', 'avg_velocity', 'weight_kg'])
                            X_pred_scaled = scaler.transform(X_pred)
                        except ImportError:
                            # Fallback to numpy array if pandas not available
                            X_pred = np.array([[avg_rom, avg_velocity, 0]])
                            X_pred_scaled = scaler.transform(X_pred)
                        
                        estimated_weight = float(model.predict(X_pred_scaled)[0])
                    except Exception as e:
                        print(f"Model prediction error: {e}")
                        # Fallback weight estimation based on ROM and tempo
                        estimated_weight = max(5.0, min(25.0, (100 - avg_rom) * 0.3 + avg_velocity * 10))
                else:
                    # Fallback weight estimation based on ROM and tempo
                    estimated_weight = max(5.0, min(25.0, (100 - avg_rom) * 0.3 + avg_velocity * 10))

            # Create info panel background
            cv2.rectangle(frame, (5, 5), (400, 280), (0, 0, 0), -1)
            cv2.rectangle(frame, (5, 5), (400, 280), (0, 255, 255), 2)
            
            # Display information with better formatting
            cv2.putText(frame, "DUMBBELL CURL TRACKER", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Left Reps: {counts['left']}", (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Right Reps: {counts['right']}", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Total: {counts['left'] + counts['right']}", (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # Arm status
            left_status = f"L: {int(left_angle_smooth)}°" if visible_left else "L: Not visible"
            right_status = f"R: {int(right_angle_smooth)}°" if visible_right else "R: Not visible"
            cv2.putText(frame, left_status, (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, right_status, (15, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Weight and time
            cv2.putText(frame, f"Weight: {estimated_weight:.1f} kg", (15, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Time: {int(elapsed // 60)}:{int(elapsed % 60):02d}", (15, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
            cv2.putText(frame, "Press 'q' to quit", (15, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            # Progress bar for time
            progress = min(elapsed / 180.0, 1.0)  # 3 minutes = 180 seconds
            bar_width = int(380 * progress)
            cv2.rectangle(frame, (10, h - 25), (390, h - 15), (50, 50, 50), -1)
            cv2.rectangle(frame, (10, h - 25), (10 + bar_width, h - 15), (0, 255, 0), -1)
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow("DeepFit - Dumbbell Curl Analysis", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

# Save workout data to MongoDB
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
data = {
    "timestamp": timestamp,
    "exercise_type": "dumbbell_curls",
    "estimated_weight": round(estimated_weight, 2),
    "left_reps": counts['left'],
    "right_reps": counts['right'],
    "total_reps": counts['left'] + counts['right'],
    "left_tempos": tempos['left'],
    "right_tempos": tempos['right'],
    "left_roms": roms['left'],
    "right_roms": roms['right'],
    "session_duration": round(elapsed, 2),
    "analysis_date": datetime.now().isoformat()
}

# Insert to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["sih2573"]
    collection = db["DumbBell"]
    result = collection.insert_one(data)
    print(f"Results saved to MongoDB with ID: {result.inserted_id}")
except Exception as e:
    print(f"Could not save to MongoDB: {e}")

cap.release()
cv2.destroyAllWindows()

print("\n" + "="*50)
print("           DUMBBELL CURL ANALYSIS COMPLETE")
print("="*50)
print(f"Session Duration: {int(elapsed // 60)}:{int(elapsed % 60):02d}")
print(f"Estimated Weight: {estimated_weight:.2f} kg")
print(f"Left Arm Reps: {counts['left']}")
print(f"Right Arm Reps: {counts['right']}")
print(f"Total Reps: {counts['left'] + counts['right']}")

if counts['left'] > 0 or counts['right'] > 0:
    print("\n" + "-"*30 + " FORM ANALYSIS " + "-"*30)
    
    for side in ['left', 'right']:
        if counts[side] > 0:
            warns = detect_cheating(estimated_weight, roms[side], tempos[side])
            print(f"\n{side.upper()} ARM ({counts[side]} reps):")
            
            if roms[side]:
                avg_rom = sum(roms[side]) / len(roms[side])
                print(f"  Average ROM: {avg_rom:.1f}°")
            
            if tempos[side]:
                avg_tempo = sum(tempos[side]) / len(tempos[side])
                print(f"  Average Tempo: {avg_tempo:.1f}s")
            
            if warns:
                print("  ⚠️  Form Issues:")
                for w in warns:
                    print(f"     • {w}")
            else:
                print("  ✅ Form looks good!")
else:
    print("\n⚠️  No reps detected. Make sure to:")
    print("   • Face the camera directly")
    print("   • Perform full range of motion")
    print("   • Keep one arm stationary while curling with the other")

print("\n" + "="*50)
print(f"Results saved to MongoDB collection: sih2573.DumbBell")
print("Press any key to close...")
input()  # Wait for user input before closing
