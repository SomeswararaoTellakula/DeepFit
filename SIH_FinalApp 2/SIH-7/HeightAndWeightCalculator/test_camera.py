#!/usr/bin/env python3
"""
Simple camera test script to verify camera functionality
"""

import cv2
import sys

def test_camera():
    """Test if camera is working"""
    print("🔍 Testing camera...")
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open camera")
        print("💡 Try these solutions:")
        print("   - Check if camera is connected")
        print("   - Close other applications using the camera")
        print("   - Try a different camera index (1, 2, etc.)")
        return False
    
    print("✅ Camera opened successfully")
    
    # Test reading frames
    ret, frame = cap.read()
    if not ret:
        print("❌ Could not read frame from camera")
        cap.release()
        return False
    
    print(f"✅ Frame captured: {frame.shape}")
    
    # Show camera feed for 5 seconds
    print("📹 Showing camera feed for 5 seconds...")
    print("   Press 'q' to quit early")
    
    import time
    start_time = time.time()
    
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if not ret:
            break
            
        cv2.putText(frame, "Camera Test - Press 'q' to quit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Camera Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("✅ Camera test completed successfully")
    return True

def main():
    """Main function"""
    print("🏋️ Situps Counter - Camera Test")
    print("=" * 40)
    
    if test_camera():
        print("\n🎉 Camera is working! You can now run the situps app.")
        print("   Run: python run_situp_app.py")
    else:
        print("\n❌ Camera test failed. Please fix camera issues first.")
        sys.exit(1)

if __name__ == "__main__":
    main()