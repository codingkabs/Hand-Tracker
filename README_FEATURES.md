# Hand Tracking Features

This project has been restructured into a modular system with a base file and multiple feature files.

## Structure

- **`base.py`** - Core hand tracking functionality (used by all features)
- **`feature_1_sign_language.py`** - Sign language letter detection
- **`feature_2_ar_ui.py`** - AR UI overlay with scary theme (original)
- **`feature_3_gesture_game.py`** - Rock Paper Scissors game
- **`feature_4_finger_counter.py`** - Finger counting display
- **`feature_5_virtual_drawing.py`** - Draw in the air with your finger
- **`feature_6_exercise_tracker.py`** - Hand exercise/rehabilitation tracker
- **`feature_7_air_piano.py`** - Virtual piano played with finger taps
- **`feature_8_pose_analyzer.py`** - Hand posture analysis and feedback
- **`feature_9_volume_control.py`** - Air volume control with pinch gesture

## How to Run

### Run Feature 1: Sign Language Detector
```bash
py -3.11 feature_1_sign_language.py
```
Detects ASL letters based on hand gestures.

### Run Feature 2: AR UI Overlay
```bash
py -3.11 feature_2_ar_ui.py
```
Original AR UI with scary red/purple theme.

### Run Feature 3: Rock Paper Scissors Game
```bash
py -3.11 feature_3_gesture_game.py
```
Play rock-paper-scissors with hand gestures (Fist=Rock, Open=Paper, V=Scissors).

### Run Feature 4: Finger Counter
```bash
py -3.11 feature_4_finger_counter.py
```
Counts and displays how many fingers are extended.

### Run Feature 5: Virtual Drawing
```bash
py -3.11 feature_5_virtual_drawing.py
```
Draw in the air! Index finger to draw, open hand to change colors, fist to clear.

### Run Feature 6: Exercise Tracker
```bash
py -3.11 feature_6_exercise_tracker.py
```
Tracks hand exercise repetitions and finger range of motion.

### Run Feature 7: Air Piano
```bash
py -3.11 feature_7_air_piano.py
```
Play virtual piano keys by pointing your index finger at them.

### Run Feature 8: Pose Analyzer
```bash
py -3.11 feature_8_pose_analyzer.py
```
Analyzes hand posture and provides feedback for ergonomics.

### Run Feature 9: Volume Control
```bash
py -3.11 feature_9_volume_control.py
```
Control volume with pinch gesture (thumb and index finger).

## Creating New Features

To create a new feature:

1. Create a new file: `feature_5_your_feature.py`
2. Import the base tracker:
   ```python
   from base import HandTracker
   ```
3. Use the tracker in your main function:
   ```python
   def main():
       tracker = HandTracker()
       tracker.start_camera()
       
       while True:
           frame, results = tracker.get_frame()
           landmarks_list = tracker.get_landmarks(results, frame.shape)
           # Your feature logic here
   ```

## Base Tracker Methods

- `start_camera()` - Initialize webcam
- `get_frame()` - Get current frame and hand detection results
- `get_landmarks()` - Extract hand landmark coordinates
- `draw_hand_skeleton()` - Draw hand connections
- `is_finger_up()` - Check if a finger is extended
- `get_finger_count()` - Count extended fingers
- `get_distance()` - Calculate distance between points
- `release()` - Clean up and close camera

