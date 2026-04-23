# DeepFit: AI-Powered Fitness & Diagnostic System

DeepFit is a comprehensive, AI-driven fitness platform designed to provide accurate health diagnostics and exercise tracking using computer vision. Built for inclusivity and security, DeepFit leverages advanced pose estimation and face verification to deliver a premium personal training experience.

## 🚀 Key Features

### 1. AI Diagnostics
- **Height & Weight Estimation**: Non-contact measurement using computer vision and anthropometric analysis.
- **Vertical Jump Analyzer**: High-precision jump height calculation with real-time feedback.

### 2. Exercise Tracking
- **Sit-up Counter**: Automated rep counting with form quality analysis.
- **Dumbbell Curl Tracker**: Dual-arm tracking with angle detection and weight estimation.

### 3. Security & Personalization
- **Identity-Based Access**: Integrated **Face Verification** system. The app compares live user frames against registration photos to gate access to diagnostics.
- **User Dashboard**: Detailed performance history and trend analysis stored in MongoDB.

### 4. Mobile Integration
- **Siri Integration (iOS)**: Launch exercises hands-free using custom AppIntents and Shortcuts.
- **Google Assistant (Android)**: Voice-activated app features via Android Shortcuts.

### 5. Inclusive Design
- Optimized interfaces and workflows for users with varying physical abilities, ensuring fitness is accessible to everyone.

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **Computer Vision**: OpenCV, MediaPipe
- **Database**: MongoDB
- **Frontend**: JavaScript (Vanilla), Modern CSS (Glassmorphism)
- **Mobile**: Swift (AppIntents), Kotlin (Android Shortcuts)

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- MongoDB (Running locally on port 27017)
- Web Camera

### 1. Clone the Repository
```bash
git clone https://github.com/SomeswararaoTellakula/DeepFit.git
cd DeepFit
```

### 2. Setup Environment
```bash
# It is recommended to use a virtual environment
python -m venv venv
source venv/bin/init  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Application
```bash
# Navigate to the core application folder
cd "SIH_FinalApp 2/SIH-7/HeightAndWeightCalculator"
python app.py
```
The app will be available at `http://localhost:5000`.

---

## 📱 Mobile Integration

Detailed setup instructions for iOS and Android can be found in:
- [iOS Setup Guide](mobile_integrations/ios/XCODE_SETUP_GUIDE.md)
- [General Testing & Setup](mobile_integrations/TESTING_AND_SETUP.md)

---

## 🔒 Identity Verification
DeepFit uses a custom **FaceVerifier** class (found in `face_verifier.py`) to ensure data privacy and security. Before starting any diagnostic exercise, the system performs a biometric check against the user's registration photo.

---

## 📄 License
This project is developed as part of the SIH 2024 Final App development. All rights reserved.
