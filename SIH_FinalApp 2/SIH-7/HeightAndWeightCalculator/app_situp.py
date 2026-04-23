from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np

app = Flask(__name__)

class SitupsCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.count = 0
        self.stage = None
        self.feedback = "Get Ready"
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0:
            angle = 360-angle
        return angle
    
    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                  landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            
            # Calculate angle
            angle = self.calculate_angle(shoulder, hip, knee)
            
            # Situp logic
            if angle > 160:
                if self.stage != "down":
                    self.stage = "down"
                    self.feedback = "Go Up!"
            elif angle < 90 and self.stage == "down":
                self.stage = "up"
                self.count += 1
                self.feedback = f"Rep {self.count}! Go Down"
            
            # Draw pose
            self.mp_draw.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            # Draw info
            cv2.putText(frame, f'Count: {self.count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, self.feedback, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f'Angle: {int(angle)}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            self.feedback = "No pose detected"
            cv2.putText(frame, self.feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame
    
    def get_stats(self):
        return {
            'reps': self.count,
            'feedback': self.feedback,
            'form_percentage': min(100, self.count * 10)
        }
    
    def reset(self):
        self.count = 0
        self.stage = None
        self.feedback = "Get Ready"

# Global variables
camera = None
counter = SitupsCounter()
is_recording = False

def generate_frames():
    global camera, is_recording
    while is_recording and camera:
        success, frame = camera.read()
        if not success:
            break
        
        frame = counter.process_frame(frame)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Main page"""
    return render_template('index_situp.html')

@app.route('/start_camera')
def start_camera():
    global camera, is_recording
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'status': 'error', 'message': 'Camera not found'})
        is_recording = True
        return jsonify({'status': 'success', 'message': 'Camera started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop_camera')
def stop_camera():
    global camera, is_recording
    is_recording = False
    if camera:
        camera.release()
        camera = None
    return jsonify({'status': 'success', 'message': 'Camera stopped'})

@app.route('/reset_counter')
def reset_counter():
    counter.reset()
    return jsonify({'status': 'success', 'message': 'Counter reset'})

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_stats')
def get_stats():
    return jsonify(counter.get_stats())

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)