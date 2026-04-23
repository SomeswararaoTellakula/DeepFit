# Installation Guide - Enhanced Height and Weight Estimation System

## 📋 Prerequisites

### System Requirements

- **Operating System**: 
  - Windows 10/11 (64-bit)
  - macOS 10.15 (Catalina) or later
  - Ubuntu 18.04 LTS or later
- **Python**: Version 3.8 to 3.11 (3.9 recommended)
- **Memory**: Minimum 8GB RAM (16GB recommended for optimal performance)
- **Storage**: At least 2GB free disk space
- **Camera**: USB webcam or built-in camera (1080p recommended)
- **Internet**: Required for initial model downloads

### Hardware Recommendations

- **CPU**: Intel i5/AMD Ryzen 5 or better
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Camera**: 1080p webcam with good low-light performance
- **Lighting**: Good ambient lighting or external lighting setup

## 🚀 Step-by-Step Installation

### Step 1: Python Installation

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and **check "Add Python to PATH"**
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.9

# Or download from python.org
```

#### Ubuntu/Linux
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.9 python3.9-pip python3.9-venv

# Verify installation
python3.9 --version
pip3 --version
```

### Step 2: Download Project Files

#### Option A: Direct Download
1. Download the project ZIP file
2. Extract to your desired location
3. Navigate to the project directory

#### Option B: Git Clone (if available)
```bash
git clone <repository-url>
cd height-weight-estimation
```

### Step 3: Create Virtual Environment

```bash
# Navigate to project directory
cd height-weight-estimation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

### Step 4: Install Dependencies

#### Automatic Installation
```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

#### Manual Installation (if automatic fails)
```bash
# Core computer vision
pip install opencv-python==4.8.1.78

# Pose estimation
pip install mediapipe==0.10.7

# Deep learning
pip install torch==2.0.1 torchvision==0.15.2

# Data processing
pip install numpy==1.24.3 pandas==2.0.3

# Machine learning
pip install scikit-learn==1.3.0

# Visualization
pip install matplotlib==3.7.2 seaborn==0.12.2

# Scientific computing
pip install scipy==1.11.1

# Configuration and serialization
pip install pyyaml==6.0.1 joblib==1.3.1
```

### Step 5: Verify Installation

```bash
# Test core imports
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import mediapipe; print('MediaPipe:', mediapipe.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"

# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
```

### Step 6: Download Pre-trained Models

The system will automatically download required models on first run:

```bash
# Run the system once to download models
python integrated_system.py
```

Models downloaded:
- MiDaS depth estimation model (~400MB)
- MediaPipe pose estimation models (~50MB)

## 🔧 Configuration

### Camera Setup

1. **Test Camera Access**:
   ```bash
   python -c "
   import cv2
   cap = cv2.VideoCapture(0)
   if cap.isOpened():
       print('Camera 0: Available')
       ret, frame = cap.read()
       if ret:
           print(f'Resolution: {frame.shape[1]}x{frame.shape[0]}')
   cap.release()
   "
   ```

2. **Multiple Cameras**:
   If you have multiple cameras, test different indices:
   ```bash
   # Test camera indices 0, 1, 2...
   python -c "
   import cv2
   for i in range(3):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f'Camera {i}: Available')
       cap.release()
   "
   ```

### GPU Setup (Optional)

For faster processing with NVIDIA GPUs:

1. **Install CUDA** (if not already installed):
   - Download from [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
   - Follow installation instructions for your OS

2. **Install PyTorch with CUDA**:
   ```bash
   # Uninstall CPU version
   pip uninstall torch torchvision
   
   # Install CUDA version (adjust for your CUDA version)
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Verify GPU Support**:
   ```bash
   python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
   ```

## 🧪 Testing Installation

### Basic Functionality Test

```bash
# Run validation system
python test_validation_system.py
```

Expected output:
- Creates `validation_results/` directory
- Generates performance charts
- Shows metrics in console

### Camera Test

```bash
# Quick camera test
python -c "
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imshow('Camera Test', frame)
    cv2.waitKey(3000)  # Show for 3 seconds
    cv2.destroyAllWindows()
    print('Camera test successful!')
else:
    print('Camera test failed!')
cap.release()
"
```

### Full System Test

```bash
# Run main application
python integrated_system.py
```

Expected behavior:
- Camera window opens
- UI elements visible
- Pose detection working
- No error messages

## 🐛 Troubleshooting

### Common Installation Issues

#### 1. Python Version Conflicts
```bash
# Check Python version
python --version

# If wrong version, use specific version
python3.9 -m venv venv
```

#### 2. Permission Errors (Windows)
```cmd
# Run as administrator or use user installation
pip install --user -r requirements.txt
```

#### 3. Camera Permission Issues

**Windows**:
- Check Windows Privacy Settings → Camera
- Allow desktop apps to access camera

**macOS**:
- System Preferences → Security & Privacy → Camera
- Grant permission to Terminal/Python

**Linux**:
```bash
# Add user to video group
sudo usermod -a -G video $USER
# Logout and login again
```

#### 4. OpenCV Installation Issues

```bash
# Alternative OpenCV installation
pip uninstall opencv-python
pip install opencv-python-headless
# Or
conda install opencv
```

#### 5. MediaPipe Installation Issues

```bash
# For older systems
pip install mediapipe==0.9.3.0

# For Apple Silicon Macs
pip install mediapipe-silicon
```

#### 6. PyTorch Installation Issues

```bash
# CPU-only version (smaller download)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Performance Issues

#### 1. Slow Processing
- Install GPU version of PyTorch
- Reduce camera resolution
- Close other applications

#### 2. Memory Issues
```bash
# Monitor memory usage
python -c "
import psutil
print(f'Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB')
"
```

#### 3. Model Download Issues
- Check internet connection
- Clear pip cache: `pip cache purge`
- Manual model download may be required

### Environment Issues

#### 1. Virtual Environment Not Activating

**Windows**:
```cmd
# If activation fails, try:
venv\Scripts\activate.bat
# Or
python -m venv venv --system-site-packages
```

**macOS/Linux**:
```bash
# If activation fails, try:
source venv/bin/activate
# Or check shell type:
echo $SHELL
```

#### 2. Package Conflicts
```bash
# Create fresh environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 📊 Verification Checklist

After installation, verify these components:

- [ ] Python 3.8+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] All packages installed without errors
- [ ] Camera accessible and working
- [ ] OpenCV can capture video frames
- [ ] MediaPipe can detect poses
- [ ] PyTorch loads without errors
- [ ] Main application starts without crashes
- [ ] UI elements display correctly
- [ ] Pose detection works in real-time
- [ ] Measurements can be taken and saved

## 🚀 Quick Start After Installation

1. **Activate Environment**:
   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Run Application**:
   ```bash
   python integrated_system.py
   ```

3. **Follow Setup Wizard**:
   - Camera calibration (recommended)
   - Position yourself according to guides
   - Take measurements

## 📞 Getting Help

If you encounter issues:

1. **Check Error Messages**: Read console output carefully
2. **Verify Requirements**: Ensure all prerequisites are met
3. **Test Components**: Use individual test scripts
4. **Check Logs**: Look for error details in console
5. **Environment**: Try fresh virtual environment

### Common Error Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Install missing package with pip |
| `Camera not found` | Check camera permissions and connections |
| `CUDA out of memory` | Use CPU version or reduce batch size |
| `Permission denied` | Run with appropriate permissions |
| `Import error` | Check Python version compatibility |

---

**Note**: Installation time varies based on internet speed and system specifications. Initial model downloads may take 10-15 minutes on first run.

