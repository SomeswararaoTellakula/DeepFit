import cv2
import numpy as np
from advanced_jump_detector import AdvancedJumpDetector

class AdvancedJumpApp:
    def __init__(self):
        self.detector = AdvancedJumpDetector()
        self.cap = None
        
    def run(self):
        """Main application loop"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties for full body view
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        cv2.namedWindow("OYSE Advanced Vertical Jump Analyzer", cv2.WINDOW_NORMAL)
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame with advanced detector
                processed_frame = self.detector.process_frame(frame)
                
                # Show frame
                cv2.imshow("OYSE Advanced Vertical Jump Analyzer", processed_frame)
                
                # Check for exit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.detector.reset_session()
                elif key == ord('s'):
                    self.detector.save_to_mongodb()
        
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        # Save data before cleanup
        self.detector.save_to_mongodb()
        
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")

if __name__ == "__main__":
    app = AdvancedJumpApp()
    app.run()