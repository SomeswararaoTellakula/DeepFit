#!/usr/bin/env python3
"""
Advanced launcher for State-of-the-Art Vertical Jump Analyzer
Powered by MediaPipe Pose Estimation & Machine Learning
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'cv2', 'numpy', 'mediapipe', 'scipy', 'sklearn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements_advanced.txt")
        print("\n🗄️ MongoDB Setup:")
        print("   Ensure MongoDB is running on localhost:27017")
        print("   Database: USER")
        print("   Collection: sih2573.Vertical_Jump")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Advanced Vertical Jump Analyzer...")
    print("   Powered by MediaPipe Pose Estimation & Machine Learning")
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        sys.exit(1)
    
    try:
        from advanced_jump_app import AdvancedJumpApp
        app = AdvancedJumpApp()
        app.run()
    except KeyboardInterrupt:
        print("\n⏹️ Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure camera is connected and not used by other applications")
        print("2. Install all dependencies: pip install -r requirements_advanced.txt")
        print("3. Check camera permissions")
        input("Press Enter to exit...")