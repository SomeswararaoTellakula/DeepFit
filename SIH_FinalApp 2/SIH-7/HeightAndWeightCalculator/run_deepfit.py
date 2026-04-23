#!/usr/bin/env python3
"""
DeepFit Situps Counter - Main Runner
Run this file to start the web application
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Timer

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def open_browser():
    """Open browser after a delay"""
    time.sleep(2)  # Wait for Flask to start
    webbrowser.open('http://localhost:5000')

def main():
    print("🏋️ Starting DeepFit Situps Counter...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this from the DeepFit directory.")
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please install manually:")
        print("pip install -r requirements.txt")
        return
    
    print("\n🚀 Starting web server...")
    print("📱 The application will open in your browser automatically")
    print("🔗 Manual URL: http://localhost:5000")
    print("\n📋 Instructions:")
    print("1. Click 'Start Camera' to begin")
    print("2. Position yourself for situps")
    print("3. Follow the on-screen feedback")
    print("4. Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser after delay
    Timer(3.0, open_browser).start()
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 DeepFit stopped. Thanks for working out!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("Please check that your camera is not being used by another application.")

if __name__ == "__main__":
    main()