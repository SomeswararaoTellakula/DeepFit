# DeepFit Situps Counter

## 🏋️ Real-time AI-powered Situps Detection and Counting

This is an enhanced version of DeepFit that focuses specifically on situps detection using computer vision and pose estimation.

## ✨ Features

- **Real-time Situps Detection**: Uses MediaPipe pose estimation to track your movements
- **Accurate Rep Counting**: Counts situps based on torso angle analysis
- **Form Feedback**: Provides real-time feedback on your form
- **Web Interface**: Clean, responsive web interface accessible from any browser
- **Progress Tracking**: Visual progress bar showing form quality percentage

## 🚀 Quick Start

### Option 1: Easy Start (Recommended)
```bash
python run_deepfit.py
```

### Option 2: Manual Start
```bash
# Install requirements
pip install -r requirements.txt

# Run the Flask app
python app.py
```

The application will automatically open in your browser at `http://localhost:5000`

## 📋 How to Use

1. **Start the Application**: Run `python run_deepfit.py`
2. **Open Browser**: Navigate to `http://localhost:5000` (opens automatically)
3. **Start Camera**: Click the "Start Camera" button
4. **Position Yourself**: 
   - Lie down on your back with knees bent
   - Keep feet flat on the ground
   - Place hands behind your head
5. **Begin Exercise**: Start doing situps following the on-screen feedback
6. **Monitor Progress**: Watch your rep count and form percentage in real-time

## 🎯 How It Works

### Pose Detection
- Uses Google's MediaPipe for real-time pose estimation
- Tracks 33 body landmarks with high accuracy
- Focuses on shoulder, hip, and knee positions for situps analysis

### Situps Detection Algorithm
1. **Angle Calculation**: Measures the angle between shoulder-hip-knee
2. **State Detection**: 
   - "Down" state: Angle > 160° (lying down)
   - "Up" state: Angle < 90° (sitting up)
3. **Rep Counting**: Increments when transitioning from "down" to "up"
4. **Form Analysis**: Provides percentage based on current angle

### Thresholds
- **Lying Down**: > 160° torso angle
- **Sitting Up**: < 90° torso angle
- **Form Quality**: Linear interpolation between thresholds

## 🛠️ Technical Details

### Dependencies
- **Flask**: Web framework for the interface
- **OpenCV**: Computer vision and video processing
- **MediaPipe**: Google's pose estimation library
- **NumPy**: Numerical computations

### File Structure
```
DeepFit/
├── app.py                 # Main Flask application
├── situps_detector.py     # Situps detection logic
├── run_deepfit.py         # Easy startup script
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── style.css          # Styling
│   └── script.js          # Frontend JavaScript
└── requirements.txt       # Python dependencies
```

## 🎨 Interface Features

- **Real-time Video Feed**: Live camera stream with pose overlay
- **Rep Counter**: Large, animated rep counter
- **Form Progress Bar**: Visual indicator of form quality
- **Feedback System**: Color-coded feedback messages
- **Responsive Design**: Works on desktop and mobile devices

## 🔧 Customization

### Adjusting Sensitivity
Edit `situps_detector.py` to modify thresholds:
```python
self.down_threshold = 160  # Lying down angle
self.up_threshold = 90     # Sitting up angle
```

### Changing Detection Side
The detector uses left-side landmarks by default. To use right-side:
```python
# Change in detect_situps method
right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, ...]
right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x, ...]
right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x, ...]
```

## 🐛 Troubleshooting

### Camera Issues
- Ensure no other applications are using the camera
- Try changing camera index in `app.py`: `cv2.VideoCapture(1)` instead of `cv2.VideoCapture(0)`

### Performance Issues
- Close other applications to free up CPU/GPU resources
- Reduce video resolution if needed
- Ensure good lighting for better pose detection

### Detection Issues
- Ensure your full torso is visible in the camera
- Maintain good lighting conditions
- Wear contrasting clothing against the background

## 📊 Accuracy Tips

For best results:
1. **Lighting**: Ensure good, even lighting
2. **Background**: Use a plain, contrasting background
3. **Positioning**: Keep your full torso visible
4. **Clothing**: Wear fitted clothing for better landmark detection
5. **Camera Angle**: Position camera to capture your side profile

## 🔄 Future Enhancements

- [ ] Multiple exercise support (pushups, squats, etc.)
- [ ] Workout session tracking
- [ ] Performance analytics
- [ ] Mobile app version
- [ ] Multi-person detection
- [ ] Voice feedback

## 📝 License

This project extends the original DeepFit framework with situps-specific functionality.

## 🤝 Contributing

Feel free to contribute improvements, bug fixes, or new features!

---

**Happy Training! 🏋️‍♀️💪**