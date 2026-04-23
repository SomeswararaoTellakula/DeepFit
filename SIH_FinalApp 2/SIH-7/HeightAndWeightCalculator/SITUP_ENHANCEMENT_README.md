# Enhanced Sit-ups Exercise Module

## Overview

The `app_situp.py` module has been enhanced with comprehensive time-constrained exercise session management, including countdown timer, video capture, and conditional result logging.

## Key Features

### ✅ 3-Minute Countdown Timer
- **Duration**: 180 seconds (configurable via `SITUP_DURATION` constant)
- **Auto-start**: Timer begins immediately when "Start Camera" is clicked
- **Real-time tracking**: Elapsed and remaining time updated every second
- **Thread-based**: Non-blocking timer implementation

### ✅ Session Management
- **Single session lock**: Prevents re-initialization during active/completed sessions
- **State tracking**: `session_active`, `session_completed` flags
- **Session isolation**: Each session is independent and tracked separately

### ✅ Video Capture Integration
- **Synchronized start**: Camera and timer start simultaneously
- **Pose detection**: Real-time sit-up counting and form analysis
- **Visual feedback**: Live form percentage and rep counting

### ✅ Manual Stop Functionality
- **Early termination**: User can stop session before timer completion
- **Immediate logging**: Results saved instantly upon manual stop
- **Session lock**: Prevents restart after manual stop
- **Elapsed time capture**: Accurate duration recording

### ✅ Auto-Save on Timer Completion
- **Automatic termination**: Session ends when timer reaches zero
- **Complete analysis**: Full pose estimation and performance metrics
- **Comprehensive scoring**: Form, range of motion, and speed control analysis

## API Endpoints

### Core Session Control
```
GET /start_camera
- Starts camera and 3-minute timer
- Returns: session status and duration
- Locks session to prevent restart

GET /stop_camera  
- Manually stops active session
- Returns: elapsed time and save status
- Marks session as completed

GET /session_status
- Returns: current session state and timing info
- Includes: active, completed, elapsed, remaining time

GET /new_session
- Resets all session variables for new session
- Only works if no active session
- Prepares system for fresh start
```

### Statistics and Monitoring
```
GET /get_stats
- Returns: real-time exercise statistics
- Includes: reps, form percentage, timing, session status

GET /video_feed
- Streams: live video with pose detection overlay
- Shows: rep count, form feedback, angle measurements
```

## Result Storage Structure

### Manual Stop Results
```json
{
    "exercise_type": "situps",
    "repetitions": 0,
    "form_score": 0,
    "duration": <elapsed_seconds>,
    "range_of_motion": 0,
    "speed_control": 0,
    "timestamp": "<ISO-8601 Timestamp>",
    "status": "manually_stopped"
}
```

### Timer Completion Results
```json
{
    "exercise_type": "situps",
    "repetitions": <actual_count>,
    "form_score": <calculated_score>,
    "duration": 180,
    "range_of_motion": <calculated_score>,
    "speed_control": <calculated_score>,
    "timestamp": "<ISO-8601 Timestamp>",
    "status": "completed"
}
```

## File Storage Locations

### Individual Session Files
```
validation_results/Exercises/Situps/performance_metrics_YYYY-MM-DDTHH-MM-SS.json
```

### Aggregate Performance File
```
validation_results/Exercises/Situps/performance.json
```

## Scoring Algorithms

### Form Score Calculation
- **Base score**: Derived from real-time form percentage
- **Rep bonus**: Minimum 60% if reps completed
- **Range**: 0-100

### Range of Motion Score
- **Angle-based**: Calculated from torso angle measurements
- **Dynamic scoring**: Based on angle variation during exercise
- **Range**: 0-100

### Speed Control Score
- **Rep-dependent**: Higher score for consistent rep completion
- **Progressive bonus**: Score increases with rep count
- **Range**: 0-100

## Session Flow States

### 1. Ready State
- `session_active = False`
- `session_completed = False`
- Camera can be started

### 2. Active State
- `session_active = True`
- `session_completed = False`
- Timer running, camera recording
- Cannot restart or reset

### 3. Completed State
- `session_active = False`
- `session_completed = True`
- Results saved, session locked
- Cannot restart without new session

## Usage Examples

### Starting a Session
```javascript
// Start camera and timer
fetch('/start_camera')
  .then(response => response.json())
  .then(data => {
    console.log(data.message); // "Camera started - 3 minute timer began"
    console.log(data.duration); // 180
  });
```

### Monitoring Progress
```javascript
// Get real-time stats
setInterval(() => {
  fetch('/get_stats')
    .then(response => response.json())
    .then(stats => {
      console.log(`Time: ${stats.elapsed_time}/${stats.remaining_time}`);
      console.log(`Reps: ${stats.reps}`);
      console.log(`Form: ${stats.form_percentage}%`);
    });
}, 1000);
```

### Manual Stop
```javascript
// Stop session early
fetch('/stop_camera')
  .then(response => response.json())
  .then(data => {
    console.log(`Stopped after ${data.elapsed_time} seconds`);
  });
```

## Configuration

### Timer Duration
```python
SITUP_DURATION = 180  # 3 minutes in seconds
```

### Results Directory
```python
RESULTS_DIR = Path("validation_results/Exercises/Situps")
```

## Error Handling

### Session State Errors
- **Already active**: Cannot start if session in progress
- **Already completed**: Cannot restart completed session
- **No active session**: Cannot stop if nothing running

### Camera Errors
- **Camera unavailable**: Graceful error handling
- **Connection issues**: Proper error messages returned

### File System Errors
- **Directory creation**: Automatic directory creation
- **Write permissions**: Error logging for file operations
- **JSON formatting**: Proper error handling for malformed data

## Testing

### Manual Testing
1. Run `python app_situp.py`
2. Navigate to `http://localhost:5001`
3. Test session flow through UI

### Automated Testing
```bash
python test_situp_enhancement.py
```

## Integration Notes

### Flask App Integration
- Seamlessly integrates with existing Flask routes
- Maintains backward compatibility
- Thread-safe implementation

### Database Integration
- Ready for MongoDB integration
- User session tracking capability
- Performance analytics support

### UI Integration
- Compatible with existing `index_situp.html`
- Real-time status updates via AJAX
- Timer display integration ready