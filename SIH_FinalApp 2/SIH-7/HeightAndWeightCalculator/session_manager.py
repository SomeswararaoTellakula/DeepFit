from functools import wraps
from flask import session, redirect, url_for, request
from bson import ObjectId
from db_config import get_db

def init_session_settings(app):
    """Initialize session settings for the Flask app"""
    from datetime import timedelta
    
    app.config.update(
        SESSION_COOKIE_SECURE=True,  # Only send cookie over HTTPS
        SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access
        SESSION_COOKIE_SAMESITE='Lax',  # Protect against CSRF
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # Session expires after 7 days
        SESSION_TYPE='filesystem'
    )

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session or 'user_id' not in session:
            # Store the requested URL for post-login redirect
            if request.endpoint:
                session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user"""
    if not session or 'user_id' not in session:
        return None
        
    try:
        db = get_db()
        if not db:
            return None
            
        user_id = ObjectId(session['user_id'])
        return db.users.find_one({'_id': user_id})
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None

def set_user_session(user):
    """Set up user session after successful login"""
    session.clear()
    session['user_id'] = str(user['_id'])
    session['user_email'] = user['email']
    session['name'] = user.get('name', 'User')
    session.permanent = True
    
    # Handle redirect after login
    next_url = session.get('next')
    if next_url:
        session.pop('next', None)
        if next_url.startswith('/'):  # Ensure URL is internal
            return next_url
    return url_for('index')