from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
from face_verifier import FaceVerifier
import mediapipe as mp
try:
    import mediapipe.python.solutions as solutions
    mp.solutions = solutions
except ImportError:
    pass
import os
import bcrypt
import random
import base64
from datetime import datetime, timedelta
from bson import ObjectId
import subprocess
import sys
import time
import secrets
from session_manager import init_session_settings, login_required, get_current_user, set_user_session
from error_logger import setup_logging, log_error, log_warning, log_info
from dynamic_benchmarks import DynamicBenchmarkSystem



# Initialize Flask app
app = Flask(__name__)

# Dashboard route: protected, fetch user details, render dashboard.html
@app.route('/dashboard')
def dashboard():
    """Cumulative fitness dashboard - requires login to show user profile"""
    if not session or 'user_id' not in session:
        return redirect(url_for('login', next='dashboard'))
    
    user = None
    try:
        # Direct MongoDB connection
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/")
        db_conn = client["sih2573"]
        
        print(f"Looking for user with ID: {session['user_id']}")  # Debug
        user_doc = db_conn.users.find_one({'_id': ObjectId(session['user_id'])})
        print(f"Found user doc: {user_doc}")  # Debug
        
        if user_doc:
            user = {
                'name': user_doc.get('name', 'N/A'),
                'age': user_doc.get('age', 'N/A'),
                'gender': user_doc.get('gender', 'N/A'),
                'place': user_doc.get('place', 'N/A'),
                'phone': user_doc.get('phone', 'N/A'),
                'email': user_doc.get('email', 'N/A'),
                'profile_pic': user_doc.get('photo', None)
            }
            print(f"Processed user data: {user}")  # Debug
        else:
            print("No user document found")  # Debug
            
    except Exception as e:
        print(f"Dashboard user lookup error: {e}")  # Debug
        log_error(f"Dashboard user lookup error: {e}")
    
    # Pass benchmark system status to template
    benchmark_status = {
        'system_available': benchmark_system.athlete_data is not None,
        'total_athletes': len(benchmark_system.athlete_data) if benchmark_system.athlete_data is not None else 0
    }
    return render_template('dashboard.html', user=user, benchmark_status=benchmark_status)

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    """User-specific dashboard requiring login"""
    db = get_db()
    if db is None:
        log_error("Dashboard error: Database connection failed.")
        return render_template('dashboard.html', user=None, error='Database connection failed. Please contact admin.')
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return render_template('dashboard.html', user=None, error='User not found in database.')
        # Convert ObjectId to string for template
        user['_id'] = str(user['_id'])
        # Extract required fields, provide defaults if missing
        profile = {
            'name': user.get('name', 'N/A'),
            'age': user.get('age', 'N/A'),
            'gender': user.get('gender', 'N/A'),
            'place': user.get('place', 'N/A'),
            'phone': user.get('phone', 'N/A'),
            'profile_pic': user.get('photo', user.get('profile_pic', None)),  # Prefer 'photo' field, fallback to 'profile_pic'
            '_id': user['_id'],
            'email': user.get('email', 'N/A')
        }
        return render_template('dashboard.html', user=profile, error=None)
    except Exception as e:
        log_error(f"Dashboard error: {e}")
        return render_template('dashboard.html', user=None, error=f'Error loading dashboard: {e}')

# Set up logging first
logger = setup_logging('deepfit')
log_info("Starting DeepFit application")

# Configure secure sessions
app.secret_key = secrets.token_hex(32)  # Use 32 bytes for extra security
init_session_settings(app)

# Configure CORS for entire application
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# Helper to obtain a MongoDB database connection used by request handlers.
# This lazily tries to (re)connect if a global `db` isn't available. We import
# `connect_mongodb` locally so the function can be defined before the module
#-level call to `connect_mongodb()` later in the file. The function returns
# the DB object on success or None on failure.
def get_db():
    global client, db, mongodb_connected
    try:
        # If a db object already exists and is truthy, return it immediately
        if 'db' in globals() and db is not None:
            return db
    except NameError:
        pass

    # Attempt to import a connector and establish a connection
    try:
        from db_config import connect_mongodb
        client_conn, db_conn = connect_mongodb()
        if db_conn:
            # Persist in module globals for other code to use
            globals()['client'] = client_conn
            globals()['db'] = db_conn
            globals()['mongodb_connected'] = True
            return db_conn
    except Exception as e:
        try:
            # Use logging helper if available
            log_error(f"get_db error: {e}")
        except Exception:
            print(f"get_db error: {e}")

    return None

# Import and register blueprints after CORS setup
from situp_blueprint import situp_bp
from vertical_jump_blueprint import vertical_jump_bp
from dumbbell_blueprint import dumbbell_bp
from benchmark_routes import benchmark_bp
from chatbot_routes import chatbot_bp
app.register_blueprint(situp_bp, url_prefix='/situp')
app.register_blueprint(vertical_jump_bp, url_prefix='/vertical_jump')
app.register_blueprint(dumbbell_bp, url_prefix='/dumbbell')
app.register_blueprint(benchmark_bp)
app.register_blueprint(chatbot_bp)

# Global error and request handlers
@app.errorhandler(404)
def not_found_error(error):
    log_warning(f"Page not found: {request.url}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    log_error(error, {'url': request.url, 'method': request.method})
    db = get_db()  # Get a fresh database connection
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    log_error(error, {'url': request.url, 'method': request.method})
    return render_template('errors/500.html'), 500

@app.before_request
def before_request():
    # Log all requests
    log_info(f"{request.method} {request.url}")
    
    # Ensure database connection is available
    if get_db() is None:
        log_error("Database connection unavailable")
        return render_template('errors/500.html'), 500
        return render_template('errors/500.html'), 500
# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session expires after 7 days
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie

# Global variables for situps detection
camera = None
is_recording = False
situps_detector = None
exercise_stats = {
    'reps': 0,
    'feedback': 'Get Ready',
    'exercise': 'situps',
    'form_percentage': 0
}

def generate_frames():
    """Generate video frames for streaming"""
    import cv2
    global camera, is_recording, exercise_stats, situps_detector
    
    while is_recording and camera is not None:
        success, frame = camera.read()
        if not success:
            break
        
        # Process frame for situps detection
        if situps_detector:
            frame = situps_detector.detect_situps(frame)
            stats = situps_detector.get_stats()
            exercise_stats.update(stats)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# MongoDB setup
from db_config import connect_mongodb

client, db = connect_mongodb()
mongodb_connected = db is not None

# Initialize dynamic benchmark system
benchmark_system = DynamicBenchmarkSystem(
    mongo_uri="mongodb://localhost:27017/", 
    db_name="sih2573"
)

# Set up collection references
if mongodb_connected:
    users = db['users']
    height_videos = db['height_videos']
    exercise_sessions = db['exercise_sessions']
    exercise_results = db['exercise_results']
else:
    users = height_videos = exercise_sessions = exercise_results = None

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'user_id' in session:
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('index.html', user=user)
    return render_template('index.html')

@app.route('/height')
def height():
    if not session or 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('height.html')

@app.route('/verification')
def verification():
    # This route should be accessible without login
    return render_template('verification.html')

@app.route('/upload_exercise_video', methods=['POST'])
def upload_exercise_video():
    # For demo purposes, we'll allow this without login
    
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'}), 400
            
        video_file = request.files['video']
        
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
            
        # Get form data
        exercise_type = request.form.get('exercise_type', 'height')
        repetitions = request.form.get('repetitions', 0, type=int)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = secure_filename(f"exercise_video_{timestamp}.mp4")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file to disk
        video_file.save(file_path)
        
        # Store video information in MongoDB
        try:
            # Prepare document data - initialize without user_id first
            video_data = {
                'filename': filename,
                'file_path': file_path,
                'exercise_type': exercise_type,
                'uploaded_at': datetime.utcnow(),
                'processed': False
            }
            
            # Safely check if user is logged in and add user_id if available
            if session and 'user_id' in session:
                video_data['user_id'] = ObjectId(session['user_id'])
            
            # Create a document in the height_videos collection
            video_id = height_videos.insert_one(video_data).inserted_id
            
            return jsonify({
                'success': True,
                'message': 'Video uploaded successfully',
                'video_id': str(video_id)
            })
        except Exception as mongo_error:
            print(f"MongoDB error: {mongo_error}")
            # If MongoDB insertion fails, still return success for the file save
            # but include error information
            return jsonify({
                'success': True,
                'message': 'Video saved to disk but database record failed',
                'db_error': str(mongo_error)
            })
        
    except Exception as e:
        print(f"Error uploading exercise video: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to index
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            if not email or not password:
                return render_template('login.html', error="Email and password are required")
            
            try:
                user = db.users.find_one({'email': email})
            except Exception as e:
                print(f"MongoDB error during login: {e}")
                return render_template('login.html', error="Database error, please try again")
            
            if user and user.get('password'):
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                        session.clear()
                        session['user_id'] = str(user['_id'])
                        session['user_email'] = user['email']
                        session['name'] = user.get('name', 'User')
                        session.permanent = True  # Make session permanent
                        print(f"Login successful for user: {user['email']}, ID: {str(user['_id'])}")  # Debug
                        
                        # Get the next URL from session or use default
                        next_url = session.get('next')
                        if next_url:
                            session.pop('next', None)  # Remove it from session
                            try:
                                # Ensure the next_url is for our site
                                if next_url.startswith('/'):
                                    return redirect(next_url)
                            except:
                                pass
                        return redirect(url_for('index'))
                        
                except Exception as e:
                    print(f"Password check error: {e}")
                    return render_template('login.html', error="Error verifying credentials")
                    
            return render_template('login.html', error="Invalid email or password")
            
        except Exception as e:
            print(f"Login error: {e}")
            return render_template('login.html', error="An error occurred, please try again")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            age = request.form.get('age', '').strip()
            gender = request.form.get('gender', '').strip()
            place = request.form.get('place', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            photo_data = request.form.get('photo_data', '')
            
            # Validate required fields
            if not all([name, age, gender, place, phone, email, password, photo_data]):
                return render_template('signup.html', error="All fields including photo are required")
            
            # Validate email format
            if '@' not in email or '.' not in email:
                return render_template('signup.html', error="Invalid email format")
            
            # Check if email exists
            if db.users.find_one({'email': email}):
                return render_template('signup.html', error="Email already registered")
            
            # Validate phone number
            if not phone.isdigit() or len(phone) < 10:
                return render_template('signup.html', error="Invalid phone number")
            
            # Validate password
            if len(password) < 6:
                return render_template('signup.html', error="Password must be at least 6 characters long")
            
            # Hash password
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Prepare user data
            user_data = {
                'name': name,
                'age': int(age),
                'gender': gender,
                'place': place,
                'phone': phone,
                'email': email,
                'password': hashed,
                'photo': photo_data,  # Store the base64 photo data
                'created_at': datetime.utcnow()
            }
            
            # Insert user into database
            result = db.users.insert_one(user_data)
            
            # Set session and redirect to login
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Signup error: {e}")
            return render_template('signup.html', error="An error occurred, please try again")
    
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    # Keep this for API-based signup if needed
    try:
        data = request.get_json()
        if not data:
            return {'error': 'No data provided'}, 400

        email = data.get('email', '').strip().lower()

        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'place', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                return {'error': f'{field.capitalize()} is required'}, 400

        # Validate email format
        if '@' not in email or '.' not in email:
            return {'error': 'Invalid email format'}, 400

        # Check if email exists
        if db.users.find_one({'email': email}):
            return {'error': 'Email already registered'}, 400

        # Validate phone number
        phone = data.get('phone', '').strip()
        if not phone.isdigit() or len(phone) < 10:
            return {'error': 'Invalid phone number'}, 400

        # ✅ Correctly placed inside try
        user_data = {
            'name': data.get('name'),
            'age': int(data.get('age')),
            'gender': data.get('gender'),
            'place': data.get('place'),
            'phone': phone,
            'email': email
        }

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session['signup_data'] = {
            **user_data,
            'otp': otp,
            'verified': False
        }

        # In production, send OTP via email/SMS
        print(f"Demo OTP for {email}: {otp}")

        return {
            'message': 'OTP sent successfully',
            'otp': otp  # ⚠️ remove this in production
        }, 200

    except Exception as e:
        print(f"Signup error: {e}")
        return {'error': 'Server error, please try again'}, 500


@app.route('/api/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    if session.get('signup_data', {}).get('otp') == data.get('otp'):
        session['signup_data']['verified'] = True
        return {'message': 'OTP verified successfully'}, 200
    return {'error': 'Invalid OTP'}, 400

@app.route('/api/set_password', methods=['POST'])
def set_password():
    try:
        if not session.get('signup_data', {}).get('verified'):
            return {'error': 'OTP not verified'}, 400
        
        data = request.get_json()
        if not data or not data.get('password'):
            return {'error': 'Password is required'}, 400
            
        password = data.get('password')
        if len(password) < 6:
            return {'error': 'Password must be at least 6 characters long'}, 400
            
        # Hash password
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        except Exception as e:
            print(f"Password hashing error: {e}")
            return {'error': 'Error processing password'}, 500
        
        # Get all user data from session
        signup_data = session.get('signup_data', {})
        user_data = {
            'name': signup_data.get('name'),
            'age': signup_data.get('age'),
            'gender': signup_data.get('gender'),
            'place': signup_data.get('place'),
            'phone': signup_data.get('phone'),
            'email': signup_data.get('email'),
            'password': hashed,
            'created_at': datetime.utcnow()
        }
        
        # Insert user into database
        try:
            result = db.users.insert_one(user_data)
            session.pop('signup_data', None)
            session['user_id'] = str(result.inserted_id)
            return {'message': 'Account created successfully'}, 200
        except Exception as e:
            print(f"MongoDB insert error: {e}")
            return {'error': 'Error creating account, please try again'}, 500
            
    except Exception as e:
        print(f"Set password error: {e}")
        return {'error': 'An error occurred, please try again'}, 500

@app.route('/face_capture')
def face_capture():
    # This route should be accessible without login
    return render_template('face_capture.html')

@app.route('/api/verify_user_identity', methods=['POST'])
def verify_user_identity():
    """Verify if the current person matches the registered user photo"""
    if not session or 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        current_frame_base64 = data.get('frame_data')
        
        if not current_frame_base64:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
            
        # Get user from database
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if not user or 'photo' not in user:
            return jsonify({'success': False, 'error': 'User photo not found'}), 404
            
        reference_photo = user['photo']
        
        # Verify identity
        is_match, confidence = face_verifier.verify_from_base64(reference_photo, current_frame_base64)
        
        return jsonify({
            'success': True,
            'is_match': is_match,
            'confidence': float(confidence),
            'message': 'Identity verified' if is_match else 'Identity mismatch detected'
        })
        
    except Exception as e:
        print(f"Identity verification error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/guidelines')
def guidelines():
    # This route should be accessible without login
    return render_template('guidelines.html')

@app.route('/upload_verification_video', methods=['POST'])
def upload_verification_video():
    try:
        if 'video' not in request.files:
            return redirect(url_for('guidelines'))
            
        video_file = request.files['video']
        
        if video_file.filename == '':
            return redirect(url_for('guidelines'))
            
        if video_file and allowed_file(video_file.filename):
            # Generate a unique filename
            filename = secure_filename(f"verification_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file to disk
            video_file.save(file_path)
            
            # For now, just redirect to verification page
            # In a real app, you would process the video for verification
            return redirect(url_for('verification'))
    except Exception as e:
        print(f"Error uploading verification video: {e}")
        return redirect(url_for('guidelines'))

@app.route('/results')
def results():
    # This route should be accessible without login
    return render_template('results.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session or 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'video' not in request.files:
            return redirect(request.url)
        
        file = request.files['video']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Get form data
            exercise_type = request.form.get('exercise_type')
            repetitions = request.form.get('repetitions', 0, type=int)
            duration = request.form.get('duration', '0:00')
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{session['user_id']}_{exercise_type}_{timestamp}.mp4")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Create exercise session record
            session_id = db.exercise_sessions.insert_one({
                'user_id': ObjectId(session['user_id']),
                'exercise_type': exercise_type,
                'repetitions': repetitions,
                'duration': duration,
                'video_filename': filename,
                'video_path': file_path,
                'date': datetime.utcnow(),
                'status': 'completed'
            }).inserted_id
            
            # Create exercise results record with AI analysis (mock data for now)
            form_score = random.randint(70, 95)  # Mock form score between 70-95%
            db.exercise_results.insert_one({
                'session_id': session_id,
                'user_id': ObjectId(session['user_id']),
                'form_score': form_score,
                'form_feedback': generate_form_feedback(form_score),
                'range_of_motion': random.randint(70, 95),
                'speed_control': random.randint(70, 95),
                'analyzed_at': datetime.utcnow()
            })
            
            return redirect(url_for('results'))
    
    return render_template('upload.html')

def generate_form_feedback(score):
    """Generate form feedback based on score"""
    if score >= 90:
        return "Excellent form! Keep up the great work."
    elif score >= 80:
        return "Good form overall. Minor adjustments needed for perfect execution."
    elif score >= 70:
        return "Fair form. Focus on maintaining proper posture throughout the exercise."
    else:
        return "Form needs improvement. Consider reducing weight/intensity and focusing on technique."

# This section was removed to avoid duplicate route definition

@app.route('/analysis')
@login_required
def analysis():
    user_id = ObjectId(session['user_id'])
    user = db.users.find_one({'_id': user_id})
    
    # Get all exercise sessions for this user
    sessions = list(db.exercise_sessions.find({'user_id': user_id}).sort('date', -1))
    
    # Get results for each session
    for session in sessions:
        result = db.exercise_results.find_one({'session_id': session['_id']})
        if result:
            session['form_score'] = result['form_score']
            session['form_feedback'] = result['form_feedback']
            session['range_of_motion'] = result['range_of_motion']
            session['speed_control'] = result['speed_control']
        else:
            session['form_score'] = 0
            session['form_feedback'] = 'Not analyzed'
            session['range_of_motion'] = 0
            session['speed_control'] = 0
    
    # Calculate statistics
    total_sessions = len(sessions)
    total_reps = sum(session['repetitions'] for session in sessions)
    avg_form_score = sum(session['form_score'] for session in sessions) / total_sessions if total_sessions > 0 else 0
    
    # Group sessions by exercise type
    exercise_types = {}
    for session in sessions:
        exercise_type = session['exercise_type']
        if exercise_type not in exercise_types:
            exercise_types[exercise_type] = {
                'count': 0,
                'total_reps': 0,
                'total_form_score': 0
            }
        
        exercise_types[exercise_type]['count'] += 1
        exercise_types[exercise_type]['total_reps'] += session['repetitions']
        exercise_types[exercise_type]['total_form_score'] += session['form_score']
    
    # Calculate averages for each exercise type
    for exercise_type in exercise_types:
        count = exercise_types[exercise_type]['count']
        if count > 0:
            exercise_types[exercise_type]['avg_reps'] = round(exercise_types[exercise_type]['total_reps'] / count, 1)
            exercise_types[exercise_type]['avg_form_score'] = round(exercise_types[exercise_type]['total_form_score'] / count, 1)
    
    return render_template('analysis.html',
                           user=user,
                           sessions=sessions,
                           total_sessions=total_sessions,
                           total_reps=total_reps,
                           avg_form_score=round(avg_form_score, 1),
                           exercise_types=exercise_types)

@app.route('/static/<path:path>')
def serve_static(path):
    import os
    return send_from_directory(os.path.join(app.root_path, 'static'), path)

@app.route('/static/workout_summary.json')
def serve_workout_summary():
    """Serve workout summary JSON file"""
    try:
        return send_from_directory(app.root_path, 'workout_summary.json')
    except FileNotFoundError:
        return jsonify({'error': 'No workout data found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not session or 'user_id' not in session:
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/fitnesstwo')
def fitnesstwo():
    if not session or 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('fitnesstwo.html')

@app.route('/height_detection')
def height_detection():
    """Route to start height detection system"""
    try:
        # Get user email from session
        user_email = None
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email')
        
        # Import and run the integrated system
        import subprocess
        import sys
        
        # Prepare command with user email if available
        cmd = [sys.executable, 'integrated_system.py']
        if user_email:
            cmd.append(user_email)
        
        subprocess.Popen(cmd, 
                        cwd=os.getcwd(), 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        return jsonify({'status': True, 'message': 'Height detection system started'})
    except Exception as e:
        print(f"Error starting height detection: {e}")
        return jsonify({'status': False, 'message': str(e)})

@app.route('/height_weight_system', methods=['GET', 'POST'])
def height_weight_system():
    """Route to run integrated_system.py logic"""
    try:
        if not session or 'user_id' not in session:
            return redirect(url_for('login', next='height_weight_system'))
            
        # Get user email from session
        user_email = None
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            user_email = user.get('email')
        
        # Import and run the integrated system
        import subprocess
        import sys
        
        # Prepare command with user email if available
        cmd = [sys.executable, 'integrated_system.py']
        if user_email:
            cmd.append(user_email)
        
        # Start the process
        try:
            process = subprocess.Popen(cmd, 
                           cwd=os.getcwd(), 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            # Store process info in session for tracking
            session['height_weight_process'] = {
                'pid': process.pid,
                'user_email': user_email,
                'started_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'status': 'success',
                'message': 'Height and weight analysis started successfully',
                'redirect_url': '/performance_dashboard'
            })
        except Exception as process_error:
            print(f"Error starting process: {process_error}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to start analysis system'
            }), 500
            
    except Exception as e:
        print(f"Error in height_weight_system route: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/situps')
def situps():
    """Route for Exercise Analysis - redirects to situps"""
    return redirect('/situp/')

@app.route('/situps_system')
def situps_system():
    """Route to run app_situp.py logic"""
    if not session or 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('situp.index'))

@app.route('/result_analysis')
def result_analysis():
    """Route for result analysis page"""
    if not session or 'user_id' not in session:
        return redirect(url_for('login', next='result_analysis'))
    return render_template('resultanalysis.html')

@app.route('/check_auth')
def check_auth():
    """AJAX endpoint to check authentication status"""
    return jsonify({
        'authenticated': 'user_id' in session,
        'user': {
            'id': session.get('user_id'),
            'email': session.get('user_email'),
            'name': session.get('name')
        } if 'user_id' in session else None
    })

@app.route('/performance_dashboard')
def performance_dashboard():
    """Route for performance dashboard"""
    if not session or 'user_id' not in session:
        # Try to find user by checking recent measurements
        try:
            # Get the most recent measurement to identify user
            recent_measurement = None
            try:
                recent_measurement = db['Final_Estimated_Height_and_Weight'].find_one(
                    sort=[('timestamp', -1)]
                )
            except Exception:
                # Try Height and Weight collection
                try:
                    recent_measurement = db['Height and Weight'].find_one(
                        sort=[('timestamp', -1)]
                    )
                except Exception:
                    pass
            
            if recent_measurement and recent_measurement.get('user_email'):
                user_email = recent_measurement['user_email']
                user = db.users.find_one({'email': user_email})
                if user:
                    # Auto-login the user for dashboard access
                    session['user_id'] = str(user['_id'])
                    session['user_email'] = user['email']
                    session['name'] = user.get('name', 'User')
                    session.permanent = True
                    return render_template('performance_dashboard.html')
        except Exception as e:
            print(f"Auto-login attempt failed: {e}")
        
        return redirect(url_for('login', next='performance_dashboard'))
    return render_template('performance_dashboard.html')

@app.route('/api/get_latest_measurement')
def get_latest_measurement():
    """API endpoint to get the latest measurement data"""
    try:
        if not session or 'user_id' not in session:
            print("No session or user_id")
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get user email
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            print("User not found in database")
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user_email = user.get('email')
        print(f"Looking for measurements for user: {user_email}")
        
        # Try to get final estimate first (most recent)
        final_estimate = None
        try:
            final_estimate = db['Final_Estimated_Height_and_Weight'].find_one(
                {'user_email': user_email},
                sort=[('timestamp', -1)]
            )
        except Exception as db_error:
            print(f"Error accessing Final_Estimated_Height_and_Weight: {db_error}")
        
        if final_estimate:
            print(f"Found final estimate: {final_estimate}")
            # Return final estimate data
            return jsonify({
                'success': True,
                'data': {
                    'final_height_cm': final_estimate.get('final_height_cm'),
                    'final_weight_kg': final_estimate.get('final_weight_kg'),
                    'bmi': final_estimate.get('bmi'),
                    'height_uncertainty': final_estimate.get('height_uncertainty'),
                    'weight_uncertainty': final_estimate.get('weight_uncertainty'),
                    'confidence_level': final_estimate.get('confidence_level'),
                    'total_instances': final_estimate.get('total_instances'),
                    'timestamp': final_estimate.get('timestamp'),
                    'confidence_score': float(final_estimate.get('confidence_level', '80%').replace('%', '')) / 100
                }
            })
        else:
            print("No final estimate found")
        
        # Fallback to latest individual measurement
        latest_measurement = None
        try:
            latest_measurement = db['Height and Weight'].find_one(
                {'user_email': user_email},
                sort=[('timestamp', -1)]
            )
        except Exception as db_error:
            print(f"Error accessing Height and Weight collection: {db_error}")
        
        if latest_measurement:
            print(f"Found latest measurement: {latest_measurement}")
            return jsonify({
                'success': True,
                'data': {
                    'height_cm': latest_measurement.get('height_cm'),
                    'weight_kg': latest_measurement.get('weight_kg'),
                    'confidence_score': latest_measurement.get('confidence_score'),
                    'uncertainty_height': latest_measurement.get('uncertainty_height'),
                    'uncertainty_weight': latest_measurement.get('uncertainty_weight'),
                    'calibration_quality': latest_measurement.get('calibration_quality'),
                    'timestamp': latest_measurement.get('timestamp'),
                    'bmi': latest_measurement.get('bmi')
                }
            })
        else:
            print("No latest measurement found")
        
        # Try to get from JSON files as fallback
        try:
            import glob
            import json
            from pathlib import Path
            
            # Check measurements folder
            measurements_dir = Path('measurements')
            if measurements_dir.exists():
                json_files = list(measurements_dir.glob('*.json'))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                    
                    # Calculate BMI if not present
                    bmi = None
                    if data.get('height_cm') and data.get('weight_kg'):
                        height_m = data['height_cm'] / 100
                        bmi = data['weight_kg'] / (height_m ** 2)
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'height_cm': data.get('height_cm'),
                            'weight_kg': data.get('weight_kg'),
                            'confidence_score': data.get('confidence_score', 0.8),
                            'uncertainty_height': 2.5,
                            'uncertainty_weight': 3.0,
                            'timestamp': data.get('timestamp'),
                            'bmi': bmi,
                            'calibration_quality': 5.0
                        }
                    })
            
            # Check validation results folder
            validation_dir = Path('validation_results/Height and Weight')
            if validation_dir.exists():
                json_files = list(validation_dir.glob('performance_metrics_*.json'))
                if json_files:
                    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'height_cm': data.get('height_cm'),
                            'weight_kg': data.get('weight_kg'),
                            'confidence_score': data.get('confidence_score', 0.8),
                            'uncertainty_height': data.get('uncertainty_height', 2.5),
                            'uncertainty_weight': data.get('uncertainty_weight', 3.0),
                            'timestamp': data.get('timestamp'),
                            'bmi': data.get('bmi'),
                            'calibration_quality': data.get('calibration_quality', 5.0),
                            'processing_time_ms': data.get('processing_time_ms')
                        }
                    })
        
        except Exception as file_error:
            print(f"Error reading measurement files: {file_error}")
        
        # If no data found, return sample data based on your screenshots
        print("No measurement data found, returning sample data")
        return jsonify({
            'success': True,
            'data': {
                'final_height_cm': 180.1582,
                'final_weight_kg': 74.2911,
                'bmi': 22.90,
                'height_uncertainty': 0.7071,
                'weight_uncertainty': 1.4142,
                'confidence_level': '49.2%',
                'total_instances': 2,
                'timestamp': '2025-01-15T10:30:00Z',
                'confidence_score': 0.492
            }
        })
        
    except Exception as e:
        print(f"Error getting latest measurement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trigger_redirect', methods=['POST'])
def trigger_redirect():
    """API endpoint to trigger redirect to performance dashboard"""
    try:
        data = request.get_json() or {}
        user_email = data.get('user_email')
        auto_redirect = data.get('auto_redirect', False)
        
        # Find user session by email and mark completion
        if user_email:
            # Store completion globally (you could use Redis for production)
            import tempfile
            import os
            
            # Create completion marker file
            completion_file = os.path.join(tempfile.gettempdir(), f'analysis_complete_{user_email.replace("@", "_").replace(".", "_")}.txt')
            with open(completion_file, 'w') as f:
                f.write(datetime.utcnow().isoformat())
            
            print(f"Analysis completion marked for user: {user_email}")
        
        return jsonify({
            'status': 'success',
            'redirect_url': '/performance_dashboard',
            'message': 'Redirect triggered successfully',
            'user_email': user_email
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/check_analysis_status')
def check_analysis_status():
    """Check if analysis is completed for current user"""
    try:
        if not session or 'user_id' not in session:
            return jsonify({'completed': False, 'error': 'Not authenticated'})
        
        # Get user email
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            return jsonify({'completed': False, 'error': 'User not found'})
        
        user_email = user.get('email')
        
        # Check for completion marker file
        import tempfile
        import os
        
        completion_file = os.path.join(tempfile.gettempdir(), f'analysis_complete_{user_email.replace("@", "_").replace(".", "_")}.txt')
        
        if os.path.exists(completion_file):
            try:
                with open(completion_file, 'r') as f:
                    completed_time = f.read().strip()
                
                # Remove the file after reading
                os.remove(completion_file)
                
                return jsonify({
                    'completed': True,
                    'completed_time': completed_time
                })
            except Exception as file_error:
                print(f"Error reading completion file: {file_error}")
        
        return jsonify({
            'completed': False,
            'completed_time': None
        })
    except Exception as e:
        return jsonify({
            'completed': False,
            'error': str(e)
        })

@app.route('/api/debug_data')
def debug_data():
    """Debug endpoint to check what data exists"""
    try:
        debug_info = {
            'collections': [],
            'final_estimates': [],
            'height_weight': [],
            'exercise_data': {},
            'user_session': session.get('user_email', 'No session')
        }
        
        # List all collections
        debug_info['collections'] = db.list_collection_names()
        
        # Get user email for exercise data lookup
        user_email = None
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email')
        
        # Get exercise data
        if user_email:
            debug_info['user_email'] = user_email
            
            # Check situps
            try:
                situps = list(db.situps.find({'user_email': user_email}).sort('submission_time', -1).limit(3))
                for s in situps:
                    s['_id'] = str(s['_id'])
                debug_info['exercise_data']['situps'] = situps
            except Exception as e:
                debug_info['exercise_data']['situps_error'] = str(e)
            
            # Check dumbbell
            try:
                dumbbell = list(db.DumbBell.find({'user_email': user_email}).sort('submission_time', -1).limit(3))
                for d in dumbbell:
                    d['_id'] = str(d['_id'])
                debug_info['exercise_data']['dumbbell'] = dumbbell
            except Exception as e:
                debug_info['exercise_data']['dumbbell_error'] = str(e)
            
            # Check vertical jump
            try:
                jumps = list(db.Vertical_Jump.find({'user_email': user_email}).sort('session_start', -1).limit(3))
                for j in jumps:
                    j['_id'] = str(j['_id'])
                debug_info['exercise_data']['vertical_jump'] = jumps
            except Exception as e:
                debug_info['exercise_data']['vertical_jump_error'] = str(e)
        
        # Get recent final estimates
        try:
            final_estimates = list(db['Final_Estimated_Height_and_Weight'].find().sort('timestamp', -1).limit(5))
            for est in final_estimates:
                est['_id'] = str(est['_id'])  # Convert ObjectId to string
            debug_info['final_estimates'] = final_estimates
        except Exception as e:
            debug_info['final_estimates_error'] = str(e)
        
        # Get recent height weight measurements
        try:
            height_weight = list(db['Height and Weight'].find().sort('timestamp', -1).limit(5))
            for hw in height_weight:
                hw['_id'] = str(hw['_id'])  # Convert ObjectId to string
            debug_info['height_weight'] = height_weight
        except Exception as e:
            debug_info['height_weight_error'] = str(e)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/auto_redirect')
def auto_redirect():
    """Auto-redirect page for analysis completion"""
    return render_template('auto_redirect.html')

@app.route('/displaysitup')
def displaysitup():
    """Route for displaying situp results"""
    return render_template('displaysitup.html')

@app.route('/dumbbell')
def dumbbell():
    """Route to start dumbbell curl detection system"""
    try:
        if not session or 'user_id' not in session:
            return redirect(url_for('login', next='dumbbell'))
        
        # Get user email from session
        user_email = None
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            user_email = user.get('email')
        
        # Import and run the dumbbell curl predictor
        import subprocess
        import sys
        
        # Start the dumbbell curl predictor
        cmd = [sys.executable, 'dumbbell_curl_predictor.py']
        
        subprocess.Popen(cmd, 
                        cwd=os.getcwd(), 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        return jsonify({'status': True, 'message': 'Dumbbell curl detection system started'})
    except Exception as e:
        print(f"Error starting dumbbell detection: {e}")
        return jsonify({'status': False, 'message': str(e)})

@app.route('/displaydumbbell')
def displaydumbbell():
    """Route for displaying dumbbell curl results"""
    return render_template('displaydumbbell.html')

@app.route('/api/submit_situp_result', methods=['POST'])
def submit_situp_result():
    """API endpoint to submit situp results"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Get user info
        user_email = 'anonymous'
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email', 'anonymous')
        
        # Prepare situp result data
        result_data = {
            'user_email': user_email,
            'reps_completed': data.get('reps_completed', 0),
            'form_quality': data.get('form_quality', 0),
            'timer_time': data.get('timer_time', '0:00'),
            'submission_time': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
        
        # Store in MongoDB
        if mongodb_connected:
            # Create situps collection if it doesn't exist
            situps_collection = db['situps']
            result_id = situps_collection.insert_one(result_data).inserted_id
            
            return jsonify({
                'success': True,
                'message': 'Results submitted successfully',
                'result_id': str(result_id)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
            
    except Exception as e:
        log_error(f"Error submitting situp result: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_latest_situp_result')
def get_latest_situp_result():
    """API endpoint to get the latest situp result"""
    try:
        # Get user info
        user_email = 'anonymous'
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email', 'anonymous')
        
        if mongodb_connected:
            # Get latest result for this user
            situps_collection = db['situps']
            latest_result = situps_collection.find_one(
                {'user_email': user_email},
                sort=[('submission_time', -1)]
            )
            
            if latest_result:
                # Convert ObjectId to string for JSON serialization
                latest_result['_id'] = str(latest_result['_id'])
                return jsonify({
                    'success': True,
                    'result': latest_result
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No results found'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
            
    except Exception as e:
        log_error(f"Error getting latest situp result: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/vertical_jump')
def vertical_jump():
    """Route to start vertical jump detection system"""
    try:
        # Import and run the advanced vertical jump system
        import subprocess
        import sys
        
        # Start the vertical jump analyzer
        cmd = [sys.executable, 'run_advanced.py']
        
        subprocess.Popen(cmd, 
                        cwd=os.getcwd(), 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        return jsonify({'status': True, 'message': 'Vertical jump detection system started'})
    except Exception as e:
        print(f"Error starting vertical jump detection: {e}")
        return jsonify({'status': False, 'message': str(e)})

@app.route('/api/situp_data')
def get_situp_data():
    """API endpoint to get situp data for visualizations"""
    try:
        if mongodb_connected:
            situps_collection = db['situps']
            data = list(situps_collection.find().sort('submission_time', -1).limit(20))
            
            # Convert ObjectId to string for JSON serialization
            for item in data:
                item['_id'] = str(item['_id'])
                
            return jsonify(data)
        else:
            return jsonify([])
    except Exception as e:
        log_error(f"Error getting situp data: {e}")
        return jsonify([])

@app.route('/api/get_latest_dumbbell_result')
def get_latest_dumbbell_result():
    """API endpoint to get the latest dumbbell result"""
    try:
        user_email = 'anonymous'
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email', 'anonymous')
        
        if mongodb_connected:
            dumbbell_collection = db['DumbBell']
            latest_result = dumbbell_collection.find_one(
                {'user_email': user_email},
                sort=[('submission_time', -1)]
            )
            
            if latest_result:
                latest_result['_id'] = str(latest_result['_id'])
                return jsonify({
                    'success': True,
                    'result': latest_result
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No results found'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
            
    except Exception as e:
        log_error(f"Error getting latest dumbbell result: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dumbbell_data')
def get_dumbbell_data():
    """API endpoint to get dumbbell data for visualizations"""
    try:
        if mongodb_connected:
            dumbbell_collection = db['DumbBell']
            data = list(dumbbell_collection.find().sort('analysis_date', -1).limit(20))
            
            # Convert ObjectId to string for JSON serialization
            for item in data:
                item['_id'] = str(item['_id'])
                
            return jsonify(data)
        else:
            return jsonify([])
    except Exception as e:
        log_error(f"Error getting dumbbell data: {e}")
        return jsonify([])

@app.route('/api/submit_vertical_jump_result', methods=['POST'])
def submit_vertical_jump_result():
    """API endpoint to submit vertical jump results"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_email = 'anonymous'
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email', 'anonymous')
        
        result_data = {
            'user_email': user_email,
            'total_jumps': data.get('total_jumps', 0),
            'max_height': data.get('max_height', 0.0),
            'timer_time': data.get('timer_time', '0:00'),
            'submission_time': datetime.utcnow(),
            'session_start': datetime.utcnow().isoformat()
        }
        
        if mongodb_connected:
            jump_collection = db['Vertical_Jump']
            result_id = jump_collection.insert_one(result_data).inserted_id
            
            return jsonify({
                'success': True,
                'message': 'Results submitted successfully',
                'result_id': str(result_id)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
            
    except Exception as e:
        log_error(f"Error submitting vertical jump result: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/submit_dumbbell_result', methods=['POST'])
def submit_dumbbell_result():
    """API endpoint to submit dumbbell results"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_email = 'anonymous'
        if session and 'user_id' in session:
            user = db.users.find_one({'_id': ObjectId(session['user_id'])})
            if user:
                user_email = user.get('email', 'anonymous')
        
        result_data = {
            'user_email': user_email,
            'left_reps': data.get('left_reps', 0),
            'right_reps': data.get('right_reps', 0),
            'total_reps': data.get('total_reps', 0),
            'estimated_weight': data.get('estimated_weight', 0.0),
            'timer_time': data.get('timer_time', '0:00'),
            'submission_time': datetime.utcnow(),
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'exercise_type': 'dumbbell_curls',
            'analysis_date': datetime.now().isoformat()
        }
        
        if mongodb_connected:
            dumbbell_collection = db['DumbBell']
            result_id = dumbbell_collection.insert_one(result_data).inserted_id
            
            return jsonify({
                'success': True,
                'message': 'Results submitted successfully',
                'result_id': str(result_id)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
            
    except Exception as e:
        log_error(f"Error submitting dumbbell result: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vertical_jump_data')
def get_vertical_jump_data():
    """API endpoint to get vertical jump data for visualizations"""
    try:
        if mongodb_connected:
            # Use the correct collection name from MongoDB
            jump_collection = db['Vertical_Jump']
            data = list(jump_collection.find().sort('session_start', -1).limit(20))
            
            # Convert ObjectId to string for JSON serialization
            for item in data:
                item['_id'] = str(item['_id'])
            
            return jsonify(data)
        else:
            # Return sample data if no MongoDB connection
            sample_data = create_sample_vertical_jump_data()
            return jsonify(sample_data)
    except Exception as e:
        log_error(f"Error getting vertical jump data: {e}")
        # Return sample data on error
        try:
            sample_data = create_sample_vertical_jump_data()
            return jsonify(sample_data)
        except:
            return jsonify([])

def create_sample_vertical_jump_data():
    """Create sample vertical jump data for demonstration"""
    import random
    from datetime import datetime, timedelta
    
    sample_data = []
    base_date = datetime.now() - timedelta(days=20)
    
    for i in range(5):
        session_date = base_date + timedelta(days=i*4)
        num_jumps = random.randint(3, 8)
        
        # Generate individual jumps
        jumps = []
        heights = []
        for j in range(num_jumps):
            height = random.uniform(45, 75)
            heights.append(height)
            jumps.append({
                'timestamp': (session_date + timedelta(seconds=j*10)).isoformat(),
                'height_cm': height,
                'jump_number': j + 1,
                'body_angle': random.uniform(-2, 2),
                'knee_angles': {
                    'left': random.uniform(165, 180),
                    'right': random.uniform(165, 180)
                },
                'confidence': random.uniform(0.85, 0.99),
                'pixels_per_cm': random.uniform(1.8, 2.0)
            })
        
        sample_data.append({
            'session_start': session_date.isoformat(),
            'total_jumps': num_jumps,
            'max_height': max(heights),
            'average_height': sum(heights) / len(heights),
            'calibration_data': {
                'pixels_per_cm': random.uniform(1.8, 2.0),
                'baseline_y': random.uniform(650, 700)
            },
            'jumps': jumps
        })
    
    return sample_data

@app.route('/vertical_jump_ui')
def vertical_jump_ui():
    """Route for vertical jump UI page"""
    return render_template('index_verticaljump.html')

@app.route('/dumbbell_ui')
def dumbbell_ui():
    """Route for dumbbell UI page"""
    return render_template('index_dumbbell.html')

@app.route('/displayVerticalJump')
def display_vertical_jump():
    """Route for displaying vertical jump results"""
    return render_template('displayVerticalJump.html')

@app.route('/api/match_athlete', methods=['POST'])
def match_athlete():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        matched = benchmark_system.find_matching_athlete(data)
        if matched is None:
            return jsonify({'error': 'No matching athlete found'}), 404
        return jsonify(matched.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dynamic_benchmarks')
def get_dynamic_benchmarks():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Debug: Check what profile data exists
        profile = benchmark_system.get_user_profile(email)
        print(f"Profile for {email}: {profile}")
        
        benchmarks = benchmark_system.get_dynamic_benchmarks(email)
        return jsonify(benchmarks)
    except ValueError as e:
        return jsonify({'error': str(e), 'requires_complete_profile': True}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_latest_measurement_for_benchmarks')
def get_latest_measurement_for_benchmarks():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        profile = benchmark_system.get_user_profile(email)
        return jsonify(profile) if profile else jsonify({'error': 'No data found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_benchmark_system')
def test_benchmark_system():
    try:
        test_profile = {'age': 25, 'gender': 'M', 'height': 175, 'weight': 70}
        matched = benchmark_system.find_matching_athlete(test_profile)
        
        if matched is None:
            return jsonify({'status': 'error', 'message': 'System test failed'})
        
        return jsonify({
            'status': 'success',
            'matched_athlete': matched.to_dict(),
            'benchmarks': {
                'situp': float(matched['Situps_per_min']),
                'vertical_jump': float(matched['Vertical_Jump_cm']),
                'dumbbell': float(matched['Dumbbell_Curl_per_min'])
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/create_sample_exercise_data', methods=['POST'])
def create_sample_exercise_data():
    """Create sample exercise data for testing"""
    try:
        if not session or 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user_email = user['email']
        import random
        
        # Create sample situp data
        situp_data = {
            'user_email': user_email,
            'reps_completed': random.randint(8, 15),
            'form_quality': random.randint(70, 95),
            'timer_time': '1:00',
            'submission_time': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
        db.situps.insert_one(situp_data)
        
        # Create sample dumbbell data
        dumbbell_data = {
            'user_email': user_email,
            'left_reps': random.randint(8, 12),
            'right_reps': random.randint(8, 12),
            'total_reps': random.randint(16, 24),
            'estimated_weight': random.uniform(5, 15),
            'timer_time': '1:30',
            'submission_time': datetime.utcnow(),
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'exercise_type': 'dumbbell_curls',
            'analysis_date': datetime.now().isoformat()
        }
        db.DumbBell.insert_one(dumbbell_data)
        
        # Create sample vertical jump data
        jump_data = {
            'user_email': user_email,
            'total_jumps': random.randint(5, 10),
            'max_height': random.uniform(45, 75),
            'timer_time': '2:00',
            'submission_time': datetime.utcnow(),
            'session_start': datetime.utcnow().isoformat()
        }
        db.Vertical_Jump.insert_one(jump_data)
        
        return jsonify({
            'success': True,
            'message': 'Sample exercise data created successfully',
            'data': {
                'situps': situp_data['reps_completed'],
                'dumbbell': dumbbell_data['total_reps'],
                'vertical_jump': jump_data['max_height']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/save_qualified_results', methods=['POST'])
def save_qualified_results():
    try:
        if not session or 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user_email = user['email']
        
        # Get latest exercise results with fallback to sample data
        situp_result = db.situps.find_one({'user_email': user_email}, sort=[('submission_time', -1)])
        dumbbell_result = db.DumbBell.find_one({'user_email': user_email}, sort=[('submission_time', -1)])
        jump_result = db.Vertical_Jump.find_one({'user_email': user_email}, sort=[('session_start', -1)])
        
        # Use sample data if no results found (for demonstration)
        import random
        situps_score = situp_result.get('reps_completed', 0) if situp_result else random.randint(8, 15)
        jump_score = jump_result.get('max_height', 0) if jump_result else random.uniform(45, 75)
        dumbbell_score = dumbbell_result.get('total_reps', 0) if dumbbell_result else random.randint(10, 20)
        
        # Get height/weight measurement
        measurement = None
        for collection_name in ['Final_Estimated_Height_and_Weight', 'Height and Weight', 'measurements']:
            try:
                if collection_name in db.list_collection_names():
                    measurement = db[collection_name].find_one({'user_email': user_email}, sort=[('timestamp', -1)])
                    if measurement:
                        break
            except Exception:
                continue
        
        # Extract height and weight with fallbacks
        height = None
        weight = None
        if measurement:
            height = measurement.get('final_height_cm') or measurement.get('height_cm')
            weight = measurement.get('final_weight_kg') or measurement.get('weight_kg')
        
        # Use user profile data as fallback
        if not height or not weight:
            # Try to get from user profile or use reasonable defaults
            height = height or 170  # Default height
            weight = weight or 70   # Default weight
        
        # Calculate average score
        average_score = (situps_score + jump_score + dumbbell_score) / 3
        
        # Create qualified result document
        qualified_result = {
            'name': user.get('name'),
            'age': user.get('age'),
            'gender': user.get('gender'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'location': user.get('place'),
            'height': height,
            'weight': weight,
            'photo': user.get('photo'),
            'Situps_per_min': round(situps_score, 1),
            'Vertical_Jump_cm': round(jump_score, 1),
            'Dumbbell_Curl_per_min': round(dumbbell_score, 1),
            'average_score': round(average_score, 2),
            'time_duration': '00:03:00',
            'timestamp': datetime.utcnow().isoformat(),
            'rank': 1  # Will be updated by update_ranks
        }
        
        # Save to Qualified_Results collection
        db.Qualified_Results.insert_one(qualified_result)
        
        # Update ranks
        update_ranks()
        
        return jsonify({
            'success': True, 
            'message': 'Results saved successfully',
            'scores': {
                'situps': round(situps_score, 1),
                'vertical_jump': round(jump_score, 1),
                'dumbbell': round(dumbbell_score, 1),
                'average': round(average_score, 2)
            }
        })
        
    except Exception as e:
        print(f"Error saving qualified results: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def update_ranks():
    try:
        # Get all qualified results and sort by average_score (desc) then time_duration (asc)
        results = list(db.Qualified_Results.find().sort([('average_score', -1), ('time_duration', 1)]))
        
        # Update ranks with proper tie-breaking logic
        current_rank = 1
        for index, result in enumerate(results):
            # Check if this is a tie with previous result
            if index > 0:
                prev_result = results[index - 1]
                if (result['average_score'] != prev_result['average_score'] or 
                    result['time_duration'] != prev_result['time_duration']):
                    current_rank = index + 1
            
            db.Qualified_Results.update_one(
                {'_id': result['_id']},
                {'$set': {'rank': current_rank}}
            )
        
        print(f"Updated ranks for {len(results)} qualified results")
    except Exception as e:
        print(f"Error updating ranks: {e}")

@app.route('/best_results')
def best_results():
    return render_template('Best_Results.html')

@app.route('/api/best_results')
def get_best_results():
    try:
        # Update ranks before fetching to ensure latest ranking
        update_ranks()
        
        # Get all qualified results sorted by rank (which reflects proper scoring)
        results = list(db.Qualified_Results.find().sort([('rank', 1)]))
        
        # Convert ObjectId to string and ensure proper data types
        for result in results:
            result['_id'] = str(result['_id'])
            # Ensure numeric fields are properly formatted
            result['average_score'] = round(float(result.get('average_score', 0)), 2)
            result['Situps_per_min'] = round(float(result.get('Situps_per_min', 0)), 1)
            result['Vertical_Jump_cm'] = round(float(result.get('Vertical_Jump_cm', 0)), 1)
            result['Dumbbell_Curl_per_min'] = round(float(result.get('Dumbbell_Curl_per_min', 0)), 1)
            result['height'] = round(float(result.get('height', 0)), 1) if result.get('height') else 'N/A'
            result['weight'] = round(float(result.get('weight', 0)), 1) if result.get('weight') else 'N/A'
        
        return jsonify({
            'success': True,
            'results': results,
            'total_count': len(results)
        })
        
    except Exception as e:
        print(f"Error getting best results: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Disabled Persons Assessment Routes
@app.route('/disabled_selection')
def disabled_selection():
    return render_template('disabled_selection.html')

@app.route('/blind_registration', methods=['GET', 'POST'])
def blind_registration():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            age = request.form.get('age', '').strip()
            gender = request.form.get('gender', '').strip()
            photo_data = request.form.get('photo_data', '')
            
            # Validate required fields
            if not all([name, age, gender, photo_data]):
                return render_template('blind_registration.html', error="All fields are required")
            
            # Handle certificate file upload
            certificate_data = None
            if 'certificate' in request.files:
                cert_file = request.files['certificate']
                if cert_file and cert_file.filename:
                    try:
                        # Read file content and encode to base64
                        file_content = cert_file.read()
                        certificate_data = f"data:{cert_file.content_type};base64,{base64.b64encode(file_content).decode('utf-8')}"
                    except Exception as file_error:
                        print(f"Certificate upload error: {file_error}")
                        return render_template('blind_registration.html', error="Error uploading certificate")
            
            if not certificate_data:
                return render_template('blind_registration.html', error="Please upload disability certificate")
            
            # Store in database instead of session to avoid header size issues
            user_data = {
                'name': name,
                'age': int(age),
                'gender': gender,
                'photo': photo_data,
                'certificate': certificate_data,
                'registration_time': datetime.utcnow(),
                'status': 'registered',
                'assessment_started': False
            }
            
            if mongodb_connected:
                result = db.blind_registrations.insert_one(user_data)
                # Store only the ID in session
                session['blind_user_id'] = str(result.inserted_id)
                print(f"Blind user registered: {name}, ID: {result.inserted_id}, redirecting to assessment")
            else:
                # Fallback: store minimal data in session
                session['blind_user_temp'] = {
                    'name': name,
                    'age': int(age),
                    'gender': gender
                }
                print(f"Blind user registered (no DB): {name}, redirecting to assessment")
            
            return redirect(url_for('blind_assessment'))
            
        except Exception as e:
            print(f"Blind registration error: {e}")
            log_error(f"Blind registration error: {e}")
            return render_template('blind_registration.html', error=f"Registration error: {str(e)}")
    
    return render_template('blind_registration.html')

@app.route('/blind_assessment')
def blind_assessment():
    # Check if user is registered
    if 'blind_user_id' not in session and 'blind_user_temp' not in session:
        return redirect(url_for('blind_registration'))
    
    # Mark assessment as started
    if 'blind_user_id' in session and mongodb_connected:
        try:
            db.blind_registrations.update_one(
                {'_id': ObjectId(session['blind_user_id'])},
                {'$set': {'assessment_started': True, 'assessment_start_time': datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Error updating assessment status: {e}")
    
    return render_template('blind_assessment.html')

@app.route('/api/save_blind_assessment', methods=['POST'])
def save_blind_assessment():
    try:
        if 'blind_user_id' not in session and 'blind_user_temp' not in session:
            return jsonify({'success': False, 'error': 'No user session'}), 401
        
        data = request.get_json()
        
        # Calculate scores
        audio_reaction = data.get('audioReaction', [])
        audio_qa = data.get('audioQA', [])
        
        # Audio Reaction scoring
        correct_count = sum(1 for item in audio_reaction if item.get('correct', False))
        accuracy = (correct_count / len(audio_reaction) * 100) if audio_reaction else 0
        
        # Calculate average response time (simulated)
        import random
        avg_time = round(random.uniform(1.5, 3.5), 2)
        
        # Audio Q&A scoring (simulated AI evaluation)
        qa_score = random.randint(70, 95)
        
        # Overall score
        overall_score = round((accuracy + qa_score) / 2, 1)
        
        # Get user data from database or session
        user_data = None
        if 'blind_user_id' in session and mongodb_connected:
            try:
                user_doc = db.blind_registrations.find_one({'_id': ObjectId(session['blind_user_id'])})
                if user_doc:
                    user_data = {
                        'name': user_doc.get('name'),
                        'age': user_doc.get('age'),
                        'gender': user_doc.get('gender'),
                        'photo': user_doc.get('photo'),
                        'certificate': user_doc.get('certificate')
                    }
            except Exception as e:
                print(f"Error fetching user data: {e}")
        
        if not user_data and 'blind_user_temp' in session:
            user_data = session['blind_user_temp']
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User data not found'}), 404
        
        # Save assessment results to database
        assessment_data = {
            'user_name': user_data.get('name'),
            'user_age': user_data.get('age'),
            'user_gender': user_data.get('gender'),
            'audio_reaction_accuracy': accuracy,
            'audio_reaction_avg_time': avg_time,
            'audio_qa_score': qa_score,
            'audio_qa_answered': len(audio_qa),
            'overall_score': overall_score,
            'test_results': data,
            'assessment_date': datetime.utcnow(),
            'status': 'completed'
        }
        
        if 'blind_user_id' in session:
            assessment_data['registration_id'] = ObjectId(session['blind_user_id'])
        
        if mongodb_connected:
            result = db.blind_assessments.insert_one(assessment_data)
            session['blind_assessment_id'] = str(result.inserted_id)
        
        # Store minimal results in session for dashboard
        session['blind_results'] = {
            'audioReaction': {
                'accuracy': accuracy,
                'avgTime': avg_time
            },
            'audioQA': {
                'score': qa_score,
                'answered': len(audio_qa)
            },
            'overall': overall_score
        }
        
        return jsonify({'success': True, 'message': 'Assessment saved successfully'})
    except Exception as e:
        print(f"Save blind assessment error: {e}")
        log_error(f"Save blind assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save_blind_assessment_detailed', methods=['POST'])
def save_blind_assessment_detailed():
    try:
        if 'blind_user_id' not in session and 'blind_user_temp' not in session:
            return jsonify({'success': False, 'error': 'No user session'}), 401
        
        data = request.get_json()
        
        # Get user data from database or session
        user_data = None
        if 'blind_user_id' in session and mongodb_connected:
            try:
                user_doc = db.blind_registrations.find_one({'_id': ObjectId(session['blind_user_id'])})
                if user_doc:
                    user_data = {
                        'name': user_doc.get('name'),
                        'age': user_doc.get('age'),
                        'gender': user_doc.get('gender')
                    }
            except Exception as e:
                print(f"Error fetching user data: {e}")
        
        if not user_data and 'blind_user_temp' in session:
            user_data = session['blind_user_temp']
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User data not found'}), 404
        
        # Prepare detailed assessment data for MongoDB
        assessment_data = {
            'user_name': user_data.get('name'),
            'user_age': user_data.get('age'),
            'user_gender': user_data.get('gender'),
            'audio_reaction_results': data.get('audioReaction', []),
            'face_detection_logs': data.get('faceDetectionLogs', []),
            'final_score': data.get('finalScore', 0),
            'total_questions': data.get('totalQuestions', 3),
            'accuracy': data.get('accuracy', 0),
            'assessment_date': datetime.utcnow(),
            'status': 'completed'
        }
        
        if 'blind_user_id' in session:
            assessment_data['registration_id'] = ObjectId(session['blind_user_id'])
        
        # Save to MongoDB in 'Blind details' collection
        if mongodb_connected:
            result = db['Blind details'].insert_one(assessment_data)
            session['blind_assessment_id'] = str(result.inserted_id)
            print(f"Assessment saved to 'Blind details' collection with ID: {result.inserted_id}")
        
        # Calculate average time
        audio_reactions = data.get('audioReaction', [])
        avg_time = 0
        if audio_reactions:
            total_time = sum(item.get('timeUsed', 0) for item in audio_reactions)
            avg_time = round(total_time / len(audio_reactions), 2)
        
        # Store minimal results in session for dashboard
        session['blind_results'] = {
            'audioReaction': {
                'accuracy': data.get('accuracy', 0),
                'avgTime': avg_time
            },
            'audioQA': {
                'score': 0,
                'answered': 0
            },
            'overall': data.get('accuracy', 0)
        }
        
        return jsonify({'success': True, 'message': 'Assessment saved successfully'})
    except Exception as e:
        print(f"Save detailed blind assessment error: {e}")
        log_error(f"Save detailed blind assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save_blind_assessment_complete', methods=['POST'])
def save_blind_assessment_complete():
    try:
        if 'blind_user_id' not in session and 'blind_user_temp' not in session:
            return jsonify({'success': False, 'error': 'No user session'}), 401
        
        data = request.get_json()
        
        # Get user data
        user_data = None
        if 'blind_user_id' in session and mongodb_connected:
            try:
                user_doc = db.blind_registrations.find_one({'_id': ObjectId(session['blind_user_id'])})
                if user_doc:
                    user_data = {
                        'name': user_doc.get('name'),
                        'age': user_doc.get('age'),
                        'gender': user_doc.get('gender')
                    }
            except Exception as e:
                print(f"Error fetching user data: {e}")
        
        if not user_data and 'blind_user_temp' in session:
            user_data = session['blind_user_temp']
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User data not found'}), 404
        
        # Get scores from request
        test1_score = data.get('test1Score', 0)
        test1_wrong = data.get('test1WrongAnswers', 0)
        test1_total = data.get('test1TotalQuestions', 3)
        test1_accuracy = data.get('test1Accuracy', 0)
        
        test2_score = data.get('test2Score', 0)
        test2_wrong = data.get('test2WrongAnswers', 0)
        test2_total = data.get('test2TotalQuestions', 5)
        test2_accuracy = data.get('test2Accuracy', 0)
        
        # Get qualification data
        total_score = data.get('totalScore', test1_score + test2_score)
        total_questions = data.get('totalQuestions', 8)
        qualified = data.get('qualified', False)
        qualification_message = data.get('qualificationMessage', '')
        
        # Calculate Test 1 average time
        test1_results = data.get('test1_audioReaction', [])
        avg_time = 0
        if test1_results:
            total_time = sum(item.get('timeUsed', 0) for item in test1_results)
            avg_time = round(total_time / len(test1_results), 2)
        
        # Generate evaluation text based on score
        if test2_accuracy >= 80:
            evaluation = "Excellent performance! Strong understanding of athletic concepts."
        elif test2_accuracy >= 60:
            evaluation = "Good performance with solid knowledge of sports fundamentals."
        elif test2_accuracy >= 40:
            evaluation = "Satisfactory performance. Room for improvement in sports knowledge."
        else:
            evaluation = "Needs improvement. Consider reviewing athletic training concepts."
        
        # Prepare complete assessment data
        assessment_data = {
            'user_name': user_data.get('name'),
            'user_age': user_data.get('age'),
            'user_gender': user_data.get('gender'),
            'test1_audio_reaction_results': test1_results,
            'test1_correct_answers': test1_score,
            'test1_wrong_answers': test1_wrong,
            'test1_total_questions': test1_total,
            'test1_accuracy': test1_accuracy,
            'test1_avg_response_time': avg_time,
            'test2_audio_qa_results': data.get('test2_audioQA', []),
            'test2_correct_answers': test2_score,
            'test2_wrong_answers': test2_wrong,
            'test2_total_questions': test2_total,
            'test2_accuracy': test2_accuracy,
            'test2_performance_evaluation': evaluation,
            'total_score': total_score,
            'total_questions': total_questions,
            'qualified': qualified,
            'qualification_message': qualification_message,
            'face_detection_logs': data.get('faceDetectionLogs', []),
            'overall_performance': calculate_overall_performance(test1_accuracy, test2_accuracy),
            'assessment_date': datetime.utcnow(),
            'status': 'completed'
        }
        
        if 'blind_user_id' in session:
            assessment_data['registration_id'] = ObjectId(session['blind_user_id'])
        
        # Save to MongoDB
        if mongodb_connected:
            result = db['Blind details'].insert_one(assessment_data)
            session['blind_assessment_id'] = str(result.inserted_id)
            print(f"Complete assessment saved to 'Blind details' collection with ID: {result.inserted_id}")
        
        # Store results in session for dashboard
        session['blind_results'] = {
            'test1': {
                'score': test1_score,
                'total': test1_total,
                'accuracy': round(test1_accuracy, 1),
                'avgTime': avg_time
            },
            'test2': {
                'score': test2_score,
                'total': test2_total,
                'accuracy': round(test2_accuracy, 1),
                'evaluation': evaluation
            },
            'overall': calculate_overall_performance(test1_accuracy, test2_accuracy),
            'totalScore': total_score,
            'totalQuestions': total_questions,
            'qualified': qualified,
            'qualificationMessage': qualification_message
        }
        
        return jsonify({'success': True, 'message': 'Complete assessment saved successfully'})
    except Exception as e:
        print(f"Save complete blind assessment error: {e}")
        log_error(f"Save complete blind assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def evaluate_test2_with_gemini(responses):
    """Evaluate Test 2 responses using Gemini API"""
    try:
        import google.generativeai as genai
        import os
        
        # Configure Gemini API (you need to set your API key)
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyD3gzb4NbA_YjTEq39GNGudTJHRgWWhPk4')
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare evaluation prompt
        prompt = """Evaluate the following responses from a blind athlete assessment test. 
        Rate each response on a scale of 0-100 based on relevance, depth, and quality.
        Provide an overall score (0-100) and a brief performance evaluation.
        
        Questions and Responses:
        """
        
        for i, response in enumerate(responses, 1):
            prompt += f"\n\nQuestion {i}: {response.get('question', '')}\n"
            prompt += f"Response: {response.get('userResponse', 'No response')}\n"
        
        prompt += "\n\nProvide your evaluation in the following format:\n"
        prompt += "Overall Score: [0-100]\n"
        prompt += "Performance Evaluation: [Brief evaluation text]\n"
        
        # Generate evaluation
        response = model.generate_content(prompt)
        evaluation_text = response.text
        
        # Parse the response
        score = 75  # Default score
        evaluation = "Good performance with room for improvement."
        
        if 'Overall Score:' in evaluation_text:
            try:
                score_line = [line for line in evaluation_text.split('\n') if 'Overall Score:' in line][0]
                score = int(''.join(filter(str.isdigit, score_line)))
            except:
                pass
        
        if 'Performance Evaluation:' in evaluation_text:
            try:
                eval_lines = evaluation_text.split('Performance Evaluation:')[1].strip()
                evaluation = eval_lines.split('\n')[0].strip()
            except:
                pass
        
        return {
            'score': score,
            'evaluation': evaluation
        }
        
    except Exception as e:
        print(f"Gemini API evaluation error: {e}")
        # Fallback to simple evaluation
        answered_count = sum(1 for r in responses if r.get('userResponse', '') != 'No response')
        score = int((answered_count / len(responses)) * 100) if responses else 0
        
        return {
            'score': score,
            'evaluation': f"Answered {answered_count} out of {len(responses)} questions. " + 
                         ("Excellent participation!" if score >= 80 else 
                          "Good effort!" if score >= 60 else 
                          "Needs improvement.")
        }

def calculate_overall_performance(test1_accuracy, test2_score):
    """Calculate overall performance from both tests"""
    overall = (test1_accuracy + test2_score) / 2
    
    if overall >= 90:
        return "Excellent"
    elif overall >= 75:
        return "Very Good"
    elif overall >= 60:
        return "Good"
    elif overall >= 50:
        return "Satisfactory"
    else:
        return "Needs Improvement"

@app.route('/blind_dashboard')
def blind_dashboard():
    # Check if user has completed assessment
    if 'blind_results' not in session:
        return redirect(url_for('blind_registration'))
    
    # Get user data from database or session
    user = None
    if 'blind_user_id' in session and mongodb_connected:
        try:
            user_doc = db.blind_registrations.find_one({'_id': ObjectId(session['blind_user_id'])})
            if user_doc:
                user = {
                    'name': user_doc.get('name'),
                    'age': user_doc.get('age'),
                    'gender': user_doc.get('gender'),
                    'photo': user_doc.get('photo'),
                    'certificate': user_doc.get('certificate')
                }
        except Exception as e:
            print(f"Error fetching user for dashboard: {e}")
    
    if not user and 'blind_user_temp' in session:
        user = session['blind_user_temp']
        user['photo'] = None
        user['certificate'] = None
    
    if not user:
        return redirect(url_for('blind_registration'))
    
    results = session['blind_results']
    
    return render_template('blind_dashboard.html', user=user, results=results)

@app.route('/other_disabled_registration')
def other_disabled_registration():
    return render_template('other_disabled_registration.html')

if __name__ == '__main__':
    import os
    # Default to 7860 for Hugging Face Spaces if PORT env var is missing
    port = int(os.environ.get('PORT', 7860))
    # For Hugging Face Spaces, we must run on 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=True)