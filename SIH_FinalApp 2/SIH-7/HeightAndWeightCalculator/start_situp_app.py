#!/usr/bin/env python3
"""
Startup script for situp app with error checking
"""

import os
import sys
import subprocess
import time
import requests

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✓ MongoDB is running")
        return True
    except Exception as e:
        print(f"✗ MongoDB error: {e}")
        return False

def check_dependencies():
    """Check if required modules are available"""
    required_modules = ['flask', 'cv2', 'pymongo']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} is available")
        except ImportError:
            print(f"✗ {module} is missing")
            return False
    
    return True

def start_app():
    """Start the Flask app"""
    print("Starting situp app...")
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies")
        return False
    
    # Check MongoDB
    mongodb_ok = check_mongodb()
    if not mongodb_ok:
        print("Warning: MongoDB not available, will use fallback user")
    
    # Start the app
    try:
        print("Starting Flask app on http://localhost:5001")
        subprocess.run([sys.executable, 'app_situp.py'], check=True)
    except KeyboardInterrupt:
        print("\nApp stopped by user")
    except Exception as e:
        print(f"Error starting app: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Situp App Startup")
    print("=" * 20)
    
    success = start_app()
    
    if not success:
        print("Failed to start app")
        sys.exit(1)