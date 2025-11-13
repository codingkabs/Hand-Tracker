"""
Feature 6: Full Body Exercise Tracker
Tracks push-ups and outlines body when standing
Author: Kabir Suri (codingkabs)
"""
import cv2
import time
import numpy as np
from pose_base import PoseTracker

class PushUpTracker:
    def __init__(self):
        self.reps = 0
        self.last_state = "up"  # "up" or "down"
        self.exercise_start_time = time.time()
        self.rep_times = []
        self.is_down = False
    
    def update(self, shoulder_y, wrist_y, hip_y):
        """Track push-up based on body position"""
        # Push-up detection: when shoulders are below wrists (down position)
        # and then back up
        
        if shoulder_y is None or wrist_y is None:
            return False
        
        # Calculate if in down position (shoulders below wrists by threshold)
        threshold = 50  # pixels
        currently_down = shoulder_y > (wrist_y + threshold)
        
        # Detect transition from up to down, then down to up = one rep
        if not self.is_down and currently_down:
            # Just went down
            self.is_down = True
        elif self.is_down and not currently_down:
            # Just came back up - count as rep
            self.reps += 1
            self.rep_times.append(time.time())
            self.is_down = False
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
        self.is_down = False

def detect_standing(landmarks_dict):
    """Detect if person is standing (hips below shoulders)"""
    if not landmarks_dict:
        return False
    
    left_shoulder = landmarks_dict.get('left_shoulder')
    right_shoulder = landmarks_dict.get('right_shoulder')
    left_hip = landmarks_dict.get('left_hip')
    right_hip = landmarks_dict.get('right_hip')
    
    if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
        return False
    
    # Average shoulder and hip positions
    avg_shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
    avg_hip_y = (left_hip[1] + right_hip[1]) / 2
    
    # Standing: hips are below shoulders
    return avg_hip_y > avg_shoulder_y

def main():
    tracker = PoseTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("=" * 60)
    print("Full Body Exercise Tracker")
    print("Author: Kabir Suri (codingkabs)")
    print("=" * 60)
    print("\nFeatures:")
    print("  - Push-up counter (detects when you go down and up)")
    print("  - Body outline when standing")
    print("  - Press 'R' to reset counter")
    print("  - Press 'F' to toggle fullscreen")
    print("  - Press ESC to exit\n")
    
    pushup_tracker = PushUpTracker()
    show_outline = False
    fullscreen = False
    
    # Create window and set to fullscreen
    cv2.namedWindow('Full Body Exercise Tracker', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Full Body Exercise Tracker', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    fullscreen = True
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Get original frame dimensions
        original_height, original_width = frame.shape[:2]
        
        # Get landmarks from original frame size
        landmarks_dict = tracker.get_landmarks(results, (original_height, original_width))
        
        # Resize frame to fill screen better
        # Get screen dimensions (adjust based on your screen resolution)
        screen_width = 1920  # Common laptop screen width
        screen_height = 1080  # Common laptop screen height
        
        # Resize frame to match screen while maintaining aspect ratio
        scale = min(screen_width / original_width, screen_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize frame
        frame = cv2.resize(frame, (new_width, new_height))
        
        # Scale landmarks to match resized frame
        if landmarks_dict:
            scale_x = new_width / original_width
            scale_y = new_height / original_height
            for key in landmarks_dict['landmarks']:
                if landmarks_dict['landmarks'][key]:
                    x, y = landmarks_dict['landmarks'][key]
                    landmarks_dict['landmarks'][key] = (int(x * scale_x), int(y * scale_y))
            # Update key points
            for key in ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                        'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee',
                        'right_knee', 'left_ankle', 'right_ankle', 'nose']:
                if landmarks_dict.get(key):
                    x, y = landmarks_dict[key]
                    landmarks_dict[key] = (int(x * scale_x), int(y * scale_y))
        
        # If frame is smaller than screen, center it on black background
        if new_width < screen_width or new_height < screen_height:
            black_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
            x_offset = (screen_width - new_width) // 2
            y_offset = (screen_height - new_height) // 2
            black_frame[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame
            frame = black_frame
            
            # Adjust landmark coordinates for centered frame
            if landmarks_dict:
                for key in landmarks_dict['landmarks']:
                    if landmarks_dict['landmarks'][key]:
                        x, y = landmarks_dict['landmarks'][key]
                        landmarks_dict['landmarks'][key] = (x + x_offset, y + y_offset)
                # Update key points
                for key in ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                            'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee',
                            'right_knee', 'left_ankle', 'right_ankle', 'nose']:
                    if landmarks_dict.get(key):
                        x, y = landmarks_dict[key]
                        landmarks_dict[key] = (x + x_offset, y + y_offset)
        
        if landmarks_dict:
            # Draw pose skeleton
            tracker.draw_pose(frame, landmarks_dict['pose_landmarks'])
            
            # Check if standing
            is_standing = detect_standing(landmarks_dict)
            if is_standing:
                show_outline = True
                # Draw body outline when standing
                tracker.draw_body_outline(frame, landmarks_dict)
            else:
                show_outline = False
            
            # Push-up detection
            left_shoulder = landmarks_dict.get('left_shoulder')
            right_shoulder = landmarks_dict.get('right_shoulder')
            left_wrist = landmarks_dict.get('left_wrist')
            right_wrist = landmarks_dict.get('right_wrist')
            left_hip = landmarks_dict.get('left_hip')
            
            # Use average of left and right for more stable detection
            if left_shoulder and right_shoulder and left_wrist and right_wrist:
                avg_shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
                avg_wrist_y = (left_wrist[1] + right_wrist[1]) / 2
                hip_y = left_hip[1] if left_hip else avg_shoulder_y
                
                # Track push-up
                rep_detected = pushup_tracker.update(avg_shoulder_y, avg_wrist_y, hip_y)
                
                if rep_detected:
                    cv2.putText(frame, "PUSH-UP!", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            
            # Display stats
            cv2.putText(frame, f'Push-ups: {pushup_tracker.reps}', (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            
            elapsed_time = time.time() - pushup_tracker.exercise_start_time
            cv2.putText(frame, f'Time: {int(elapsed_time)}s', (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            if pushup_tracker.reps > 0:
                avg_time = pushup_tracker.get_average_rep_time()
                cv2.putText(frame, f'Avg: {avg_time:.1f}s/rep', (50, 140), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Status indicator
            if show_outline:
                cv2.putText(frame, "STANDING - Body Outline Active", 
                           (50, frame.shape[0] - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "PUSH-UP MODE", 
                           (50, frame.shape[0] - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # Progress bar
            bar_width = 300
            bar_height = 30
            bar_x = 50
            bar_y = frame.shape[0] - 100
            
            # Draw background
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            
            # Draw progress (based on reps, goal of 10)
            goal = 10
            progress = min((pushup_tracker.reps / goal) * 100, 100)
            progress_width = int(bar_width * (progress / 100))
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
            
            cv2.putText(frame, f'Progress: {pushup_tracker.reps}/{goal} ({int(progress)}%)', 
                       (bar_x, bar_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        else:
            # No body detected
            cv2.putText(frame, "No body detected - Stand in front of camera", 
                       (50, frame.shape[0] // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Press 'R' to reset | ESC to exit", 
                   (50, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Full Body Exercise Tracker', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('r') or key == ord('R'):  # Reset
            pushup_tracker.reset()
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
