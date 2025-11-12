# Hand Tracking AR UI - Modular Feature System

A comprehensive hand tracking project featuring multiple AR/VR applications built with Python, OpenCV, and MediaPipe. This project uses a modular architecture with a base hand tracking system and multiple feature implementations.

## 🎯 Features

This project includes **9 different hand tracking applications**:

1. **Sign Language Detector** - Detects ASL letters in real-time
2. **AR UI Overlay** - Futuristic AR interface with scary theme
3. **Rock Paper Scissors Game** - Play with hand gestures
4. **Finger Counter** - Count and display extended fingers
5. **Virtual Drawing** - Draw in the air with color controls
6. **Exercise Tracker** - Track hand exercises and range of motion
7. **Air Piano** - Play virtual piano with finger taps
8. **Pose Analyzer** - Analyze hand posture for ergonomics
9. **Volume Control** - Control volume with pinch gestures

## 🚀 Quick Start

### Prerequisites
- Python 3.8 - 3.11 (MediaPipe doesn't support Python 3.12+ yet)
- Webcam/Camera

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Hand-Tracking-AR-UI-main
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. **Run a feature:**
   ```bash
   # Windows
   py -3.11 feature_1_sign_language.py
   
   # Linux/Mac
   python3 feature_1_sign_language.py
   ```

   Or run the main launcher:
   ```bash
   py -3.11 main.py
   ```

## 📁 Project Structure

```
Hand-Tracking-AR-UI-main/
├── base.py                      # Core hand tracking class (used by all features)
├── main.py                      # Main launcher with AR UI (original style)
├── feature_1_sign_language.py   # Sign language detection
├── feature_2_ar_ui.py           # AR UI overlay (scary theme)
├── feature_3_gesture_game.py    # Rock Paper Scissors game
├── feature_4_finger_counter.py  # Finger counting display
├── feature_5_virtual_drawing.py # Virtual air drawing
├── feature_6_exercise_tracker.py # Exercise/rehabilitation tracker
├── feature_7_air_piano.py       # Virtual piano
├── feature_8_pose_analyzer.py  # Hand posture analyzer
├── feature_9_volume_control.py # Air volume control
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎮 Usage

### Running Individual Features

Each feature can be run independently:

```bash
# Sign Language Detector
py -3.11 feature_1_sign_language.py

# AR UI Overlay
py -3.11 feature_2_ar_ui.py

# Rock Paper Scissors
py -3.11 feature_3_gesture_game.py

# Finger Counter
py -3.11 feature_4_finger_counter.py

# Virtual Drawing
py -3.11 feature_5_virtual_drawing.py

# Exercise Tracker
py -3.11 feature_6_exercise_tracker.py

# Air Piano
py -3.11 feature_7_air_piano.py

# Pose Analyzer
py -3.11 feature_8_pose_analyzer.py

# Volume Control
py -3.11 feature_9_volume_control.py
```

### Main Launcher

Run `main.py` for the original AR UI experience with enhanced features.

**Controls:**
- **Open Hand** - Full AR UI overlay with all graphics
- **Pinch Gesture** - Shows pinch intensity with arcs
- **Fist** - Simple glowing circle indicator
- **ESC** - Exit application

## 🛠️ Technologies Used

- **Python 3.8-3.11** - Programming language
- **OpenCV** - Computer vision and image processing
- **MediaPipe** - Hand tracking and pose estimation
- **NumPy** - Numerical computations

## 🎨 Customization

All features use the modular `base.py` class, making it easy to:
- Create new features by extending the base class
- Modify existing features
- Share common hand tracking functionality

See `README_FEATURES.md` for detailed documentation on creating new features.

## 📝 Notes

- **Python Version**: Use Python 3.8-3.11. MediaPipe doesn't support Python 3.12+ yet.
- **Camera Access**: Make sure to allow webcam access when prompted.
- **Performance**: Works best in good lighting conditions.
- **Gestures**: Some features require specific hand gestures - see individual feature documentation.

## 👤 Author

**Kabir Suri (codingkabs)**

## 📄 License

MIT License - feel free to use this project for learning and development!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new features
- Improve existing features
- Fix bugs
- Enhance documentation

---

**Enjoy exploring the world of hand tracking and AR/VR interfaces!** 🚀
