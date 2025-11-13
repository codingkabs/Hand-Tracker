"""
Feature 6: Full Body Exercise Tracker with Calibration
Tracks exercises with position calibration for accurate rep counting
Author: Kabir Suri (codingkabs)
"""
import cv2
import time
import numpy as np
from pose_base import PoseTracker

class ExerciseTracker:
    def __init__(self):
        self.reps = 0
        self.exercise_start_time = time.time()
        self.rep_times = []
        self.position_1 = None  # First position (e.g., up for push-ups)
        self.position_2 = None  # Second position (e.g., down for push-ups)
        self.current_state = "position_1"  # Which position we're currently in
        self.is_calibrated = False
    
    def set_position_1(self, key_point_y):
        """Set the first position (e.g., up position)"""
        self.position_1 = key_point_y
    
    def set_position_2(self, key_point_y):
        """Set the second position (e.g., down position)"""
        self.position_2 = key_point_y
        self.is_calibrated = True
    
    def update(self, current_y):
        """Track reps based on calibrated positions"""
        if not self.is_calibrated or self.position_1 is None or self.position_2 is None:
            return False
        
        # Calculate thresholds (midpoint between positions)
        threshold = (self.position_1 + self.position_2) / 2
        
        # Determine which position we're closer to
        dist_to_pos1 = abs(current_y - self.position_1)
        dist_to_pos2 = abs(current_y - self.position_2)
        
        # Determine current state
        if dist_to_pos1 < dist_to_pos2:
            new_state = "position_1"
        else:
            new_state = "position_2"
        
        # Detect transition: position_1 -> position_2 -> position_1 = one rep
        if self.current_state == "position_1" and new_state == "position_2":
            # Moved from position 1 to position 2
            self.current_state = "position_2"
        elif self.current_state == "position_2" and new_state == "position_1":
            # Completed a rep! (went from pos2 back to pos1)
            self.reps += 1
            self.rep_times.append(time.time())
            self.current_state = "position_1"
            return True
        
        return False
    
    def get_average_rep_time(self):
        """Calculate average time per rep"""
        if len(self.rep_times) < 2:
            return 0
        intervals = [self.rep_times[i] - self.rep_times[i-1] 
                   for i in range(1, len(self.rep_times))]
        return sum(intervals) / len(intervals) if intervals else 0
    
    def reset(self):
        """Reset tracker"""
        self.reps = 0
        self.rep_times = []
        self.exercise_start_time = time.time()
        self.is_calibrated = False
        self.position_1 = None
        self.position_2 = None
        self.current_state = "position_1"

def get_key_point_y(landmarks_dict, exercise_type="pushup"):
    """Get the key point Y coordinate based on exercise type"""
    if not landmarks_dict:
        return None
    
    if exercise_type == "pushup":
        # For push-ups, use average shoulder Y position
        left_shoulder = landmarks_dict.get('left_shoulder')
        right_shoulder = landmarks_dict.get('right_shoulder')
        if left_shoulder and right_shoulder:
            return (left_shoulder[1] + right_shoulder[1]) / 2
    elif exercise_type == "shoulder_raise":
        # For shoulder raises, use average wrist Y position
        left_wrist = landmarks_dict.get('left_wrist')
        right_wrist = landmarks_dict.get('right_wrist')
        if left_wrist and right_wrist:
            return (left_wrist[1] + right_wrist[1]) / 2
    elif exercise_type == "squat":
        # For squats, use average hip Y position
        left_hip = landmarks_dict.get('left_hip')
        right_hip = landmarks_dict.get('right_hip')
        if left_hip and right_hip:
            return (left_hip[1] + right_hip[1]) / 2
    
    return None

def draw_countdown(frame, countdown_number, message=""):
    """Draw countdown on frame"""
    text = str(countdown_number) if countdown_number > 0 else "GO!"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 5, 10)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = (frame.shape[0] + text_size[1]) // 2
    
    # Background
    cv2.rectangle(frame, (text_x - 50, text_y - text_size[1] - 50),
                 (text_x + text_size[0] + 50, text_y + 50), (0, 0, 0), -1)
    
    # Countdown text
    color = (0, 255, 0) if countdown_number == 0 else (0, 255, 255)
    cv2.putText(frame, text, (text_x, text_y),
               cv2.FONT_HERSHEY_SIMPLEX, 5, color, 10)
    
    # Message
    if message:
        msg_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        msg_x = (frame.shape[1] - msg_size[0]) // 2
        cv2.putText(frame, message, (msg_x, text_y - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

def main():
    tracker = PoseTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("=" * 60)
    print("Full Body Exercise Tracker with Calibration")
    print("Author: Kabir Suri (codingkabs)")
    print("=" * 60)
    print("\nCalibration Process:")
    print("  1. Countdown 3, 2, 1 - Get into FIRST position (e.g., up)")
    print("  2. Countdown 3, 2, 1 - Get into SECOND position (e.g., down)")
    print("  3. Start exercising - Reps will be counted automatically")
    print("\nControls:")
    print("  - Press 'C' to recalibrate")
    print("  - Press 'R' to reset counter")
    print("  - Press 'F' to toggle fullscreen")
    print("  - Press ESC to exit\n")
    
    exercise_tracker = ExerciseTracker()
    exercise_type = "pushup"  # Can be "pushup", "shoulder_raise", "squat"
    
    # Calibration state machine
    calibration_state = "waiting"  # waiting, countdown_1, capture_1, countdown_2, capture_2, exercising
    countdown_number = 3
    countdown_start_time = 0
    capture_duration = 1.0  # How long to capture position (1 second)
    capture_start_time = 0
    captured_positions = []
    
    fullscreen = False
    cv2.namedWindow('Full Body Exercise Tracker', cv2.WINDOW_NORMAL)
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Get original frame dimensions
        original_height, original_width = frame.shape[:2]
        
        # Get landmarks
        landmarks_dict = tracker.get_landmarks(results, frame.shape)
        
        # Resize for fullscreen if enabled
        screen_width = 1920
        screen_height = 1080
        scale = min(screen_width / original_width, screen_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        frame = cv2.resize(frame, (new_width, new_height))
        
        # Scale landmarks
        if landmarks_dict:
            scale_x = new_width / original_width
            scale_y = new_height / original_height
            for key in landmarks_dict['landmarks']:
                if landmarks_dict['landmarks'][key]:
                    x, y = landmarks_dict['landmarks'][key]
                    landmarks_dict['landmarks'][key] = (int(x * scale_x), int(y * scale_y))
            for key in ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                        'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee',
                        'right_knee', 'left_ankle', 'right_ankle', 'nose']:
                if landmarks_dict.get(key):
                    x, y = landmarks_dict[key]
                    landmarks_dict[key] = (int(x * scale_x), int(y * scale_y))
        
        # Center frame if needed
        if new_width < screen_width or new_height < screen_height:
            black_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
            x_offset = (screen_width - new_width) // 2
            y_offset = (screen_height - new_height) // 2
            black_frame[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame
            frame = black_frame
            if landmarks_dict:
                for key in landmarks_dict['landmarks']:
                    if landmarks_dict['landmarks'][key]:
                        x, y = landmarks_dict['landmarks'][key]
                        landmarks_dict['landmarks'][key] = (x + x_offset, y + y_offset)
                for key in ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                            'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee',
                            'right_knee', 'left_ankle', 'right_ankle', 'nose']:
                    if landmarks_dict.get(key):
                        x, y = landmarks_dict[key]
                        landmarks_dict[key] = (x + x_offset, y + y_offset)
        
        current_time = time.time()
        
        # Draw pose if detected
        if landmarks_dict:
            tracker.draw_pose(frame, landmarks_dict['pose_landmarks'])
        
        # Calibration state machine
        if calibration_state == "waiting":
            cv2.putText(frame, "Press 'C' to start calibration", 
                       (frame.shape[1] // 2 - 200, frame.shape[0] // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            calibration_state = "ready"
        
        elif calibration_state == "countdown_1":
            elapsed = current_time - countdown_start_time
            if elapsed >= 1.0 and countdown_number > 0:
                countdown_number -= 1
                countdown_start_time = current_time
                elapsed = 0
            
            draw_countdown(frame, countdown_number, "Get into FIRST position")
            
            if countdown_number == 0 and elapsed >= 0.5:
                calibration_state = "capture_1"
                capture_start_time = current_time
                captured_positions = []
                countdown_number = 3
        
        elif calibration_state == "capture_1":
            # Capture position for 1 second
            if landmarks_dict:
                key_y = get_key_point_y(landmarks_dict, exercise_type)
                if key_y is not None:
                    captured_positions.append(key_y)
            
            elapsed = current_time - capture_start_time
            if elapsed >= capture_duration:
                # Average the captured positions
                if captured_positions:
                    avg_y = sum(captured_positions) / len(captured_positions)
                    exercise_tracker.set_position_1(avg_y)
                    cv2.putText(frame, "FIRST POSITION CAPTURED!", 
                               (frame.shape[1] // 2 - 250, frame.shape[0] // 2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    time.sleep(1)
                
                calibration_state = "countdown_2"
                countdown_start_time = current_time
                countdown_number = 3
        
        elif calibration_state == "countdown_2":
            elapsed = current_time - countdown_start_time
            if elapsed >= 1.0 and countdown_number > 0:
                countdown_number -= 1
                countdown_start_time = current_time
                elapsed = 0
            
            draw_countdown(frame, countdown_number, "Get into SECOND position")
            
            if countdown_number == 0 and elapsed >= 0.5:
                calibration_state = "capture_2"
                capture_start_time = current_time
                captured_positions = []
                countdown_number = 3
        
        elif calibration_state == "capture_2":
            # Capture position for 1 second
            if landmarks_dict:
                key_y = get_key_point_y(landmarks_dict, exercise_type)
                if key_y is not None:
                    captured_positions.append(key_y)
            
            elapsed = current_time - capture_start_time
            if elapsed >= capture_duration:
                # Average the captured positions
                if captured_positions:
                    avg_y = sum(captured_positions) / len(captured_positions)
                    exercise_tracker.set_position_2(avg_y)
                    cv2.putText(frame, "SECOND POSITION CAPTURED!", 
                               (frame.shape[1] // 2 - 250, frame.shape[0] // 2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    time.sleep(1)
                
                calibration_state = "exercising"
                exercise_tracker.exercise_start_time = current_time
        
        elif calibration_state == "exercising":
            # Track exercise reps
            if landmarks_dict and exercise_tracker.is_calibrated:
                key_y = get_key_point_y(landmarks_dict, exercise_type)
                if key_y is not None:
                    rep_detected = exercise_tracker.update(key_y)
                    
                    if rep_detected:
                        cv2.putText(frame, "REP!", 
                                   (frame.shape[1] // 2 - 100, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
            
            # Display stats
            cv2.putText(frame, f'Reps: {exercise_tracker.reps}', (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            
            elapsed_time = current_time - exercise_tracker.exercise_start_time
            cv2.putText(frame, f'Time: {int(elapsed_time)}s', (50, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            
            if exercise_tracker.reps > 0:
                avg_time = exercise_tracker.get_average_rep_time()
                cv2.putText(frame, f'Avg: {avg_time:.1f}s/rep', (50, 170), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            # Show current position indicator
            if landmarks_dict and exercise_tracker.is_calibrated:
                key_y = get_key_point_y(landmarks_dict, exercise_type)
                if key_y is not None:
                    dist_to_pos1 = abs(key_y - exercise_tracker.position_1)
                    dist_to_pos2 = abs(key_y - exercise_tracker.position_2)
                    
                    if dist_to_pos1 < dist_to_pos2:
                        pos_text = "Position 1"
                        pos_color = (0, 255, 255)
                    else:
                        pos_text = "Position 2"
                        pos_color = (255, 0, 255)
                    
                    cv2.putText(frame, pos_text, (50, frame.shape[0] - 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, pos_color, 3)
            
            # Progress bar
            bar_width = 400
            bar_height = 40
            bar_x = 50
            bar_y = frame.shape[0] - 150
            
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            
            goal = 10
            progress = min((exercise_tracker.reps / goal) * 100, 100)
            progress_width = int(bar_width * (progress / 100))
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
            
            cv2.putText(frame, f'Progress: {exercise_tracker.reps}/{goal} ({int(progress)}%)', 
                       (bar_x, bar_y - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Instructions
        if calibration_state == "exercising":
            cv2.putText(frame, "Press 'C' to recalibrate | 'R' to reset | ESC to exit", 
                       (50, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "Press 'C' to calibrate | ESC to exit", 
                       (50, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow('Full Body Exercise Tracker', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('c') or key == ord('C'):  # Calibrate
            exercise_tracker.reset()
            calibration_state = "countdown_1"
            countdown_number = 3
            countdown_start_time = current_time
        elif key == ord('r') or key == ord('R'):  # Reset
            exercise_tracker.reset()
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty('Full Body Exercise Tracker', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty('Full Body Exercise Tracker', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    
    tracker.release()
    print("\nExercise session ended!")

if __name__ == "__main__":
    main()
