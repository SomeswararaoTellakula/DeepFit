# User Manual - Enhanced Height and Weight Estimation System

## 🎯 Getting Started

### First Time Setup

1. **Launch the Application**:
   ```bash
   python integrated_system.py
   ```

2. **Camera Calibration** (Highly Recommended):
   - The system will prompt for calibration on first run
   - Print a chessboard pattern (9x6 squares, 25mm each)
   - Follow the on-screen calibration wizard
   - This significantly improves measurement accuracy

3. **Test Your Setup**:
   - Stand 2-3 meters from the camera
   - Ensure good lighting
   - Verify full body is visible in the frame

## 🎮 User Interface Guide

### Main Interface Elements

#### 1. Camera View
- **Live Video Feed**: Real-time camera input
- **Pose Detection**: Green skeleton overlay when detected
- **Visual Guides**: Positioning aids and alignment helpers

#### 2. Status Bar (Top)
- **Current Status**: Detection and measurement status
- **Calibration Info**: Camera calibration quality
- **FPS Counter**: Real-time performance indicator

#### 3. Positioning Guides (Overlay)
- **Body Zone Indicators**: Colored rectangles for optimal positioning
- **Center Alignment**: Crosshairs and center lines
- **Distance Scale**: Right-side distance indicator

#### 4. Measurement Panel (Bottom Left)
- **Height**: Current height estimate with uncertainty
- **Weight**: Current weight estimate with uncertainty  
- **BMI**: Body Mass Index calculation and category
- **Confidence**: Measurement accuracy indicator

#### 5. Controls Panel (Top Right)
- **Keyboard Shortcuts**: Available commands
- **Current Settings**: Auto-save status and options

### Visual Feedback System

#### Color Coding
- **🟢 Green**: Good detection, optimal positioning
- **🟡 Yellow**: Partial detection, needs adjustment
- **🔴 Red**: Poor detection, major adjustment needed
- **🔵 Blue**: Information, neutral status

#### Status Messages
- **"STEP INTO THE FRAME"**: No human detected
- **"ADJUST POSITION"**: Partial body visible
- **"PERFECT POSITION"**: Ready for measurement
- **"MEASURING"**: Taking stable measurement

## 📐 Taking Measurements

### Optimal Setup

#### Camera Positioning
1. **Height**: Camera at chest level (1.2-1.5m high)
2. **Distance**: 2-3 meters from subject
3. **Angle**: Camera perpendicular to subject
4. **Stability**: Secure, non-moving camera mount

#### Lighting Conditions
1. **Even Lighting**: Avoid harsh shadows
2. **Sufficient Brightness**: Well-lit environment
3. **Avoid Backlighting**: Don't stand in front of bright windows
4. **Consistent**: Stable lighting throughout measurement

#### Background
1. **Plain Background**: Solid color preferred
2. **Contrasting**: Different from clothing color
3. **Uncluttered**: Remove distracting objects
4. **Stable**: Non-moving background elements

### Subject Positioning

#### Standing Position
1. **Upright Posture**: Stand straight, shoulders back
2. **Arms Position**: Arms slightly away from body
3. **Feet**: Shoulder-width apart, both feet visible
4. **Facing Camera**: Look directly at camera
5. **Clothing**: Form-fitting clothes for better detection

#### What to Avoid
- ❌ Loose, baggy clothing
- ❌ Hats or head coverings
- ❌ Sitting or crouching
- ❌ Partial body in frame
- ❌ Moving during measurement

### Measurement Process

#### Step 1: Position Yourself
1. Stand in the designated area
2. Follow the visual positioning guides
3. Ensure all body parts are visible
4. Wait for "PERFECT POSITION" status

#### Step 2: Hold Still
1. Remain stationary for 3-5 seconds
2. Watch the stability indicator
3. Breathe normally, don't hold breath
4. Wait for measurement completion

#### Step 3: Review Results
1. Check the measurement panel
2. Note the confidence score
3. Review uncertainty estimates
4. Save if satisfied with results

## ⌨️ Keyboard Controls

### Primary Controls
- **'Q'**: Quit application
- **'S'**: Save current measurement
- **'R'**: Reset stability buffer
- **'C'**: Toggle auto-save mode
- **'K'**: Recalibrate camera

### Advanced Controls
- **'ESC'**: Emergency exit
- **'SPACE'**: Pause/resume processing
- **'F'**: Toggle fullscreen mode
- **'H'**: Show/hide help overlay

## 🔧 Settings and Configuration

### Auto-Save Mode
- **Enabled**: Automatically saves stable measurements
- **Cooldown**: 10-second delay between auto-saves
- **Toggle**: Press 'C' to enable/disable

### Stability Settings
- **Threshold**: 8 consecutive stable frames required
- **Tolerance**: ±1cm height, ±0.8kg weight variation
- **Reset**: Press 'R' to restart stability counting

### Camera Settings
- **Resolution**: 1280x720 (HD) default
- **Frame Rate**: 30 FPS target
- **Calibration**: Automatic loading of saved calibration

## 📊 Understanding Results

### Measurement Display

#### Height Measurement
```
Height: 175.5 ± 1.2 cm
```
- **175.5 cm**: Estimated height
- **± 1.2 cm**: Uncertainty range (173.3 - 177.7 cm)

#### Weight Measurement
```
Weight: 68.2 ± 2.1 kg
```
- **68.2 kg**: Estimated weight
- **± 2.1 kg**: Uncertainty range (66.1 - 70.3 kg)

#### BMI Calculation
```
BMI: 22.3 (Normal)
```
- **22.3**: Body Mass Index value
- **Normal**: Category (Underweight/Normal/Overweight/Obese)

#### Confidence Score
```
Accuracy: ████████░░ 82.0%
```
- **Visual Bar**: Graphical confidence indicator
- **82.0%**: Numerical confidence percentage

### Interpreting Confidence Scores

| Score Range | Interpretation | Action |
|-------------|----------------|---------|
| 90-100% | Excellent | High confidence, save measurement |
| 80-89% | Good | Reliable measurement |
| 70-79% | Fair | Consider retaking |
| 60-69% | Poor | Improve conditions |
| <60% | Very Poor | Check setup and positioning |

### Uncertainty Estimates

#### Height Uncertainty
- **<1.5 cm**: Excellent precision
- **1.5-3.0 cm**: Good precision
- **3.0-5.0 cm**: Fair precision
- **>5.0 cm**: Poor precision, retake measurement

#### Weight Uncertainty
- **<2.0 kg**: Excellent precision
- **2.0-4.0 kg**: Good precision
- **4.0-6.0 kg**: Fair precision
- **>6.0 kg**: Poor precision, retake measurement

## 🎯 Camera Calibration

### When to Calibrate
- **First Use**: Always calibrate new cameras
- **Poor Accuracy**: If measurements seem consistently off
- **Camera Changes**: After moving or adjusting camera
- **Periodic**: Monthly calibration for best results

### Calibration Process

#### Preparation
1. **Print Chessboard**: 9x6 squares, 25mm each square
2. **Mount Pattern**: On flat, rigid surface
3. **Good Lighting**: Even illumination of pattern
4. **Clear View**: Ensure pattern is fully visible

#### Calibration Steps
1. **Start Calibration**: Press 'K' or follow first-run prompt
2. **Position Pattern**: Hold chessboard in camera view
3. **Wait for Detection**: Green overlay indicates detection
4. **Capture Images**: Press SPACE when pattern detected
5. **Multiple Angles**: Capture 15+ images from different positions
6. **Complete**: Press ESC when finished

#### Calibration Tips
- **Vary Positions**: Different distances and angles
- **Cover Frame**: Use entire camera field of view
- **Steady Hands**: Keep pattern stable during capture
- **Good Detection**: Only capture when pattern is clearly detected

### Calibration Quality

#### Reprojection Error
- **<0.5 pixels**: Excellent calibration
- **0.5-1.0 pixels**: Good calibration
- **1.0-2.0 pixels**: Fair calibration
- **>2.0 pixels**: Poor calibration, recalibrate

## 📈 Improving Accuracy

### Environmental Optimization

#### Lighting Setup
1. **Multiple Sources**: Use several light sources
2. **Diffused Light**: Avoid harsh, direct lighting
3. **Even Coverage**: Eliminate shadows
4. **Consistent**: Maintain same lighting for all measurements

#### Camera Setup
1. **Stable Mount**: Use tripod or stable surface
2. **Optimal Height**: Camera at subject's chest level
3. **Perpendicular**: Camera facing subject directly
4. **Clean Lens**: Keep camera lens clean

#### Background Setup
1. **Solid Color**: Use plain wall or backdrop
2. **Contrasting**: Choose color different from clothing
3. **Non-Reflective**: Avoid shiny or reflective surfaces
4. **Stationary**: Ensure background doesn't move

### Subject Preparation

#### Clothing Guidelines
1. **Form-Fitting**: Avoid loose, baggy clothes
2. **Contrasting**: Different color from background
3. **Minimal Layers**: Remove jackets, sweaters
4. **No Accessories**: Remove hats, large jewelry

#### Positioning Tips
1. **Natural Stance**: Stand normally, don't pose
2. **Relaxed**: Keep shoulders and arms relaxed
3. **Centered**: Use alignment guides for positioning
4. **Stable**: Remain still during measurement

### Technical Optimization

#### System Performance
1. **Close Applications**: Free up system resources
2. **Good Hardware**: Use recommended specifications
3. **GPU Acceleration**: Enable if available
4. **Regular Updates**: Keep software updated

#### Measurement Technique
1. **Multiple Readings**: Take several measurements
2. **Consistent Conditions**: Use same setup each time
3. **Patience**: Wait for stable readings
4. **Review Results**: Check confidence scores

## 🐛 Troubleshooting

### Common Issues

#### "No Human Detected"
**Causes:**
- Poor lighting conditions
- Subject too far from camera
- Obstructed view of subject
- Camera not working properly

**Solutions:**
- Improve lighting
- Move closer to camera (2-3 meters)
- Remove obstructions
- Check camera connection

#### "Partial Body Visible"
**Causes:**
- Subject too close to camera
- Parts of body outside frame
- Poor pose detection
- Clothing interference

**Solutions:**
- Step back from camera
- Adjust position to show full body
- Improve lighting
- Wear form-fitting clothes

#### Low Confidence Scores
**Causes:**
- Poor environmental conditions
- Suboptimal positioning
- Camera not calibrated
- System performance issues

**Solutions:**
- Follow setup guidelines
- Calibrate camera
- Improve lighting and background
- Check system resources

#### Inconsistent Measurements
**Causes:**
- Changing conditions between measurements
- Poor stability during measurement
- Camera movement
- Clothing differences

**Solutions:**
- Maintain consistent setup
- Hold still during measurement
- Secure camera mount
- Use similar clothing

### Error Messages

#### Camera Errors
- **"Camera not found"**: Check camera connection
- **"Camera permission denied"**: Grant camera access
- **"Camera in use"**: Close other camera applications

#### Processing Errors
- **"Model loading failed"**: Check internet connection
- **"Insufficient memory"**: Close other applications
- **"GPU error"**: Switch to CPU processing

#### Calibration Errors
- **"Pattern not detected"**: Check chessboard pattern
- **"Insufficient images"**: Capture more calibration images
- **"Calibration failed"**: Retry with better conditions

## 💾 Data Management

### Saving Measurements

#### Manual Save
- Press 'S' to save current measurement
- Measurements saved to `measurements.csv`
- Includes timestamp and all measurement data

#### Auto-Save
- Toggle with 'C' key
- Automatically saves stable measurements
- 10-second cooldown between saves

#### Data Format
```csv
timestamp,height_cm,weight_kg,bmi,confidence,uncertainty_height,uncertainty_weight
2024-01-15 14:30:25,175.5,68.2,22.3,0.85,1.2,2.1
```

### Exported Data

#### Measurement History
- **Location**: `measurements.csv`
- **Format**: CSV (Excel compatible)
- **Contents**: All measurement data with timestamps

#### Calibration Data
- **Location**: `camera_calibration.yaml`
- **Format**: YAML configuration file
- **Contents**: Camera intrinsic parameters

#### Validation Results
- **Location**: `validation_results/`
- **Contents**: Performance analysis and charts
- **Generated**: When running validation tests

## 🔒 Privacy and Security

### Data Collection
- **Local Processing**: All processing done on your device
- **No Cloud Upload**: Measurements stay on your computer
- **No Personal Info**: Only height/weight measurements stored

### Camera Access
- **Permission Required**: System requests camera access
- **Local Only**: Video never leaves your device
- **No Recording**: Live processing only, no video saved

### Data Storage
- **Local Files**: All data stored locally
- **User Control**: You control all saved data
- **Easy Deletion**: Simply delete measurement files

## 📞 Support and Help

### Getting Help
1. **Check Manual**: Review relevant sections
2. **Run Diagnostics**: Use built-in test functions
3. **Check Logs**: Review console output for errors
4. **Verify Setup**: Ensure proper installation

### Performance Expectations
- **Height Accuracy**: ±2-4 cm typical
- **Weight Accuracy**: ±3-6 kg typical
- **Processing Speed**: 150-300ms per frame
- **Success Rate**: >95% under good conditions

### Limitations
- **Single Camera**: Inherent depth estimation limitations
- **Individual Variation**: Body composition affects weight accuracy
- **Environmental Sensitivity**: Lighting and positioning critical
- **Clothing Effects**: Loose clothing reduces accuracy

---

**Remember**: This system provides estimates based on computer vision analysis. For medical or official purposes, use professional measurement equipment.

