"""
Feature 6: Hand Exercise/Rehabilitation Tracker
Tracks finger movements and exercise repetitions
"""
import cv2
import time
import numpy as np
from base import HandTracker

class ExerciseTracker:
    def __init__(self):
        self.reps = 0
        self.last_finger_count = 0
        self.exercise_start_time = time.time()
        self.rep_times = []
        self.current_exercise = "Finger Spread"
    
    def update(self, finger_count):
        """Track finger movements for exercise counting"""
        # Detect when fingers go from closed to open (one rep)
        if self.last_finger_count == 0 and finger_count >= 4:
            self.reps += 1
            self.rep_times.append(time.time())
            return True
        self.last_finger_count = finger_count
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
        self.last_finger_count = 0

def calculate_finger_angles(landmarks, tracker):
    """Calculate angles for each finger joint"""
    angles = {}
    
    for finger_name in ['index', 'middle', 'ring', 'pinky']:
        finger_points = landmarks['fingers'][finger_name]
        if len(finger_points) >= 3:
            # Calculate angle at middle joint
            p1 = np.array(finger_points[0])
            p2 = np.array(finger_points[1])
            p3 = np.array(finger_points[2])
            
            v1 = p1 - p2
            v2 = p3 - p2
            
            try:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
                angles[finger_name] = angle
            except:
                angles[finger_name] = 0
    
    return angles

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Hand Exercise Tracker - Press ESC to exit")
    print("Exercise: Open and close your hand repeatedly")
    print("Make a fist to reset counter")
    
    exercise_tracker = ExerciseTracker()
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            finger_count = tracker.get_finger_count(landmarks)
            
            # Reset on fist
            if finger_count == 0 and exercise_tracker.reps > 0:
                if time.time() - exercise_tracker.exercise_start_time > 2:
                    exercise_tracker.reset()
                    cv2.putText(frame, "RESET!", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            # Track exercise
            rep_detected = exercise_tracker.update(finger_count)
            if rep_detected:
                cv2.putText(frame, "REP!", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            
            # Calculate finger angles for range of motion
            angles = calculate_finger_angles(landmarks, tracker)
            
            # Display stats
            cv2.putText(frame, f'Reps: {exercise_tracker.reps}', (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            
            elapsed_time = time.time() - exercise_tracker.exercise_start_time
            cv2.putText(frame, f'Time: {int(elapsed_time)}s', (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            if exercise_tracker.reps > 0:
                avg_time = exercise_tracker.get_average_rep_time()
                cv2.putText(frame, f'Avg: {avg_time:.1f}s/rep', (50, 140), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Show finger angles
            y_offset = 200
            for finger, angle in angles.items():
                cv2.putText(frame, f'{finger.capitalize()}: {int(angle)}°', 
                           (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                           (200, 200, 200), 2)
                y_offset += 25
            
            # Progress bar
            bar_width = 300
            bar_height = 30
            bar_x = 50
            bar_y = frame.shape[0] - 60
            
            # Draw background
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            
            # Draw progress (based on reps)
            progress = min(exercise_tracker.reps * 10, 100)
            progress_width = int(bar_width * (progress / 100))
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
            
            cv2.putText(frame, f'Progress: {progress}%', (bar_x, bar_y - 10), 
                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Hand Exercise Tracker', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

