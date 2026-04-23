# MongoDB Integration for Height & Weight System

## Overview

The `integrated_system.py` has been refactored to eliminate direct user input prompts and instead retrieve authenticated user data directly from MongoDB after successful login.

## Key Changes

### ✅ Removed User Input Prompts
- No more `input()` calls for User ID, Gender, Age, Height, Weight
- System automatically retrieves user data from MongoDB
- Seamless integration with Flask authentication system

### 🔐 Authentication Flow
1. User logs in through Flask web interface
2. Flask stores user session with user_id
3. When launching integrated system, Flask passes user email as command line argument
4. Integrated system connects to MongoDB and retrieves user profile data

### 📊 User Data Retrieved from MongoDB
- **User ID**: Email address (used as primary identifier)
- **Gender**: M/F/Other
- **Age**: Numeric age
- **Name**: Full name for display
- **Photo**: Profile photo (URL or base64 data)

### ❌ Data NOT Retrieved
- **Height**: Will be measured by the system
- **Weight**: Will be measured by the system

## Technical Implementation

### MongoDB Manager Class
```python
class MongoDBManager:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['sih2573']
        self.users = self.db['users']
    
    def get_user_by_email(self, email):
        return self.users.find_one({'email': email.lower().strip()})
```

### Updated System Initialization
```python
system = IntegratedHeightWeightSystem(
    use_gpu=True,
    calibration_file="camera_calibration.yaml",
    user_email="user@example.com"  # Passed from Flask
)
```

### Flask Integration
```python
@app.route('/height_weight_system')
def height_weight_system():
    # Get user email from session
    user_email = None
    if session and 'user_id' in session:
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            user_email = user.get('email')
    
    # Launch integrated system with user email
    cmd = [sys.executable, 'integrated_system.py']
    if user_email:
        cmd.append(user_email)
    
    subprocess.Popen(cmd, ...)
```

## Usage

### From Flask Web Interface
1. User logs in through web interface
2. Navigate to height detection page
3. Click "Start Height Detection" button
4. System automatically launches with user data

### Command Line (for testing)
```bash
# With authenticated user
python integrated_system.py user@example.com

# Anonymous mode
python integrated_system.py
```

### Testing MongoDB Integration
```bash
python test_mongodb_integration.py
```

## Database Schema

The system expects users in MongoDB with this structure:
```json
{
    "_id": ObjectId("..."),
    "name": "John Doe",
    "age": 25,
    "gender": "M",
    "email": "john@example.com",
    "photo": "base64_or_url_data",
    "created_at": ISODate("...")
}
```

## Error Handling

### MongoDB Connection Failure
- System gracefully falls back to anonymous mode
- Displays warning message but continues operation
- All measurement functionality remains available

### User Not Found
- System operates in anonymous mode
- Measurements still saved with timestamp-based user ID
- No demographic data included in saved files

### Authentication Bypass
- System can run without authentication for testing
- Anonymous measurements saved to separate files
- Full functionality maintained

## Benefits

### ✅ Improved User Experience
- No manual data entry required
- Seamless integration with web authentication
- Automatic user identification

### ✅ Data Consistency
- Single source of truth (MongoDB)
- Consistent user data across all systems
- Reduced data entry errors

### ✅ Security
- No sensitive data stored in measurement files
- User authentication handled by Flask
- Secure session management

### ✅ Flexibility
- Works with or without authentication
- Graceful degradation for testing
- Backward compatibility maintained

## Configuration

### MongoDB Connection
Default connection: `mongodb://localhost:27017/`
Database: `sih2573`
Collection: `users`

### Required Dependencies
```
pymongo>=4.0.0
```

### Environment Setup
1. Ensure MongoDB is running
2. Verify database and collection exist
3. Test connection with test script

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB status
mongod --version
mongo --eval "db.runCommand('ping')"

# Test connection
python test_mongodb_integration.py
```

### User Data Issues
- Verify user exists in database
- Check email format matches exactly
- Ensure required fields are present

### Flask Integration Issues
- Verify session management is working
- Check user_id is properly stored in session
- Ensure ObjectId conversion is correct