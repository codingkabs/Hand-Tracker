"""
Feature 8: Smart Hand Pose Analyzer
Analyzes hand posture and provides feedback
"""
import cv2
import numpy as np
import time
from base import HandTracker

class PoseAnalyzer:
    def __init__(self):
        self.good_posture_count = 0
        self.bad_posture_count = 0
        self.last_reminder_time = 0
    
    def analyze_posture(self, landmarks, tracker):
        """Analyze hand posture and return feedback"""
        feedback = []
        score = 100
        
        # Check finger extension (good posture = relaxed, not fully extended)
        finger_angles = []
        for finger_name in ['index', 'middle', 'ring', 'pinky']:
            finger_points = landmarks['fingers'][finger_name]
            if len(finger_points) >= 3:
                p1 = np.array(finger_points[0])
                p2 = np.array(finger_points[1])
                p3 = np.array(finger_points[2])
                
                v1 = p1 - p2
                v2 = p3 - p2
                
                try:
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                    angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
                    finger_angles.append(angle)
                except:
                    pass
        
        if finger_angles:
            avg_angle = np.mean(finger_angles)
            # Good angle range: 120-160 degrees (relaxed)
            if avg_angle < 100:
                feedback.append("Fingers too curled - relax your hand")
                score -= 20
            elif avg_angle > 170:
                feedback.append("Fingers too extended - relax your hand")
                score -= 20
            else:
                feedback.append("Good finger position!")
        
        # Check wrist angle
        wrist = landmarks['wrist']
        middle_mcp = landmarks['landmarks'][9]
        middle_pip = landmarks['landmarks'][10]
        
        wrist_angle = np.degrees(np.arctan2(
            middle_pip[1] - middle_mcp[1],
            middle_pip[0] - middle_mcp[0]
        ))
        
        # Check for excessive wrist bend
        if abs(wrist_angle) > 45:
            feedback.append("Wrist bent too much - keep it straight")
            score -= 15
        
        # Check thumb position
        thumb_tip = landmarks['thumb_tip']
        index_mcp = landmarks['landmarks'][5]
        thumb_distance = tracker.get_distance(thumb_tip, index_mcp)
        
        if thumb_distance > 100:
            feedback.append("Thumb too far - relax position")
            score -= 10
        
        # Overall assessment
        if score >= 80:
            self.good_posture_count += 1
            status = "GOOD POSTURE"
            status_color = (0, 255, 0)
        elif score >= 60:
            status = "OK POSTURE"
            status_color = (0, 255, 255)
        else:
            self.bad_posture_count += 1
            status = "POOR POSTURE"
            status_color = (0, 0, 255)
        
        return {
            'score': score,
            'status': status,
            'status_color': status_color,
            'feedback': feedback
        }

def main():
    tracker = HandTracker()
    analyzer = PoseAnalyzer()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Hand Pose Analyzer - Press ESC to exit")
    print("Keep your hand in a relaxed, natural position")
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Analyze posture
            analysis = analyzer.analyze_posture(landmarks, tracker)
            
            # Display score
            score = analysis['score']
            cv2.putText(frame, f'Posture Score: {score}/100', (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, analysis['status_color'], 3)
            
            # Display status
            cv2.putText(frame, analysis['status'], (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, analysis['status_color'], 2)
            
            # Display feedback
            y_offset = 150
            for i, feedback_text in enumerate(analysis['feedback'][:3]):  # Show max 3 feedback items
                color = (0, 255, 0) if "Good" in feedback_text else (0, 0, 255)
                cv2.putText(frame, f'• {feedback_text}', (50, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                y_offset += 30
            
            # Statistics
            total = analyzer.good_posture_count + analyzer.bad_posture_count
            if total > 0:
                good_percent = (analyzer.good_posture_count / total) * 100
                cv2.putText(frame, f'Good: {analyzer.good_posture_count} | Bad: {analyzer.bad_posture_count}', 
                           (50, frame.shape[0] - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f'Good Posture Rate: {good_percent:.1f}%', 
                           (50, frame.shape[0] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Progress bar
            bar_width = 300
            bar_height = 20
            bar_x = 50
            bar_y = frame.shape[0] - 100
            
            # Background
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
            
            # Score bar
            score_width = int(bar_width * (score / 100))
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + score_width, bar_y + bar_height), 
                         analysis['status_color'], -1)
            
            # Border
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        cv2.imshow('Hand Pose Analyzer', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

