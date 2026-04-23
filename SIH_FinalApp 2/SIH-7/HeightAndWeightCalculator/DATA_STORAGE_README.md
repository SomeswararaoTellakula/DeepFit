# Enhanced Data Storage System

## Overview

The `integrated_system.py` has been enhanced with comprehensive data storage functionality that automatically saves measurement results and user data to structured JSON files.

## Directory Structure

All data is saved under the `validation_results/` directory with the following structure:

```
validation_results/
├── Height and Weight/
│   ├── performance.json                         # Aggregate metrics
│   ├── demographics.json                        # Static user data
│   └── performance_metrics_<timestamp>.json     # Session-specific metrics
│
└── Exercises/
    └── Situps/
        ├── performance.json                     # Aggregate performance metrics
        ├── demographics.json                    # User metadata
        └── performance_metrics_<timestamp>.json # Timestamped session metrics
```

## Enhanced Features

### 1. 'S' Key Functionality
- Press 'S' during measurement to save current results
- Automatically creates JSON files with structured data
- Includes performance metrics, user data, and measurement details

### 2. Auto-Save Capability
- Automatically saves stable measurements when enabled
- Configurable cooldown period between auto-saves
- Toggle with 'C' key during operation

### 3. User Demographics Collection
- Optional user data collection at startup
- Stores age, gender, height, weight for analysis
- Automatically generates user IDs if not provided

### 4. File Structure

#### performance.json (Aggregate)
```json
{
    "total_sessions": 1,
    "metrics": [...],
    "last_updated": "2025-09-12T12:47:06.498028"
}
```

#### demographics.json
```json
{
    "user_id": "test_user_001",
    "age": 25,
    "gender": "M",
    "height": 175.0,
    "weight": 70.0,
    "last_updated": "2025-09-12T12:47:06.499079"
}
```

#### performance_metrics_<timestamp>.json
```json
{
    "timestamp": "2025-09-12T12-47-06",
    "height_cm": 175.5,
    "weight_kg": 70.2,
    "confidence_score": 0.85,
    "uncertainty_height": 2.1,
    "uncertainty_weight": 3.5,
    "processing_time_ms": 150.0,
    "detection_status": "good_position",
    "calibration_quality": 0.5,
    "bmi": 22.79
}
```

## Usage

### Running the System
```bash
python integrated_system.py
```

### Controls
- **'Q'**: Quit application
- **'S'**: Save current measurement to JSON files
- **'R'**: Reset stability buffer
- **'C'**: Toggle auto-save mode
- **'K'**: Recalibrate camera

### Testing Data Storage
```bash
python test_data_storage.py
```

## Error Handling

- All file operations are wrapped in try/except blocks
- Graceful handling of write errors
- Automatic directory creation if missing
- UTF-8 encoding for international character support

## File Management

- Timestamped files prevent overwriting
- Aggregate files keep last 100 sessions to prevent bloat
- JSON format with 4-space indentation for readability
- ISO 8601 timestamp format for consistency

## Integration Notes

- Seamlessly integrated with existing measurement system
- No impact on real-time performance
- Optional user data collection
- Backward compatible with existing functionality