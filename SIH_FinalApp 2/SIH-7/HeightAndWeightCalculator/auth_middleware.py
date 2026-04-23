from functools import wraps
from flask import session, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not session.get('user_id'):
            # Store the requested URL in the session
            session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
