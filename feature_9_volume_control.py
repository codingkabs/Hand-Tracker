"""
Feature 9: Air Volume Control
Control volume with hand gestures (pinch to adjust)
"""
import cv2
import numpy as np
from base import HandTracker
from fullscreen_helper import setup_fullscreen_window, resize_frame_for_fullscreen, toggle_fullscreen

class VolumeControl:
    def __init__(self):
        self.volume = 50  # 0-100
        self.last_pinch_dist = None
        self.is_controlling = False
    
    def update_volume(self, pinch_dist, min_dist=20, max_dist=100):
        """Update volume based on pinch distance"""
        if self.last_pinch_dist is None:
            self.last_pinch_dist = pinch_dist
            return
        
        # Normalize pinch distance to 0-100
        normalized = np.clip((pinch_dist - min_dist) / (max_dist - min_dist) * 100, 0, 100)
        self.volume = int(100 - normalized)  # Invert: closer = higher volume
        self.last_pinch_dist = pinch_dist
    
    def reset(self):
        """Reset control state"""
        self.last_pinch_dist = None
        self.is_controlling = False

def draw_volume_bar(frame, volume, center):
    """Draw a circular volume indicator"""
    # Outer circle
    cv2.circle(frame, center, 80, (100, 100, 100), 3)
    
    # Volume arc (green to red)
    start_angle = -90
    end_angle = start_angle + int(360 * (volume / 100))
    
    # Draw volume arc
    for angle in range(start_angle, end_angle, 5):
        rad = np.deg2rad(angle)
        x1 = int(center[0] + 70 * np.cos(rad))
        y1 = int(center[1] + 70 * np.sin(rad))
        x2 = int(center[0] + 80 * np.cos(rad))
        y2 = int(center[1] + 80 * np.sin(rad))
        
        # Color gradient: green (0) to yellow (50) to red (100)
        if volume < 50:
            color = (0, int(255 * (volume / 50)), 255 - int(255 * (volume / 50)))
        else:
            color = (0, 255 - int(255 * ((volume - 50) / 50)), int(255 * ((volume - 50) / 50)))
        
        cv2.line(frame, (x1, y1), (x2, y2), color, 3)
    
    # Volume text
    cv2.putText(frame, f'{volume}%', (center[0] - 40, center[1] + 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Volume label
    cv2.putText(frame, 'VOLUME', (center[0] - 50, center[1] - 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def main():
    tracker = HandTracker()
    volume_control = VolumeControl()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Air Volume Control - Press ESC to exit")
    print("Press 'F' to toggle fullscreen")
    print("Pinch thumb and index finger to adjust volume")
    print("Open hand to stop controlling")
    
    fullscreen = setup_fullscreen_window('Air Volume Control', start_fullscreen=False)
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            palm = landmarks['palm']
            thumb_tip = landmarks['thumb_tip']
            index_tip = landmarks['index_tip']
            
            # Calculate pinch distance
            pinch_dist = tracker.get_distance(thumb_tip, index_tip)
            
            finger_count = tracker.get_finger_count(landmarks)
            
            # Control volume when pinching
            if pinch_dist < 80 and finger_count <= 2:
                volume_control.is_controlling = True
                volume_control.update_volume(pinch_dist)
                
                # Draw connection line
                cv2.line(frame, thumb_tip, index_tip, (0, 255, 0), 3)
                cv2.circle(frame, thumb_tip, 10, (0, 255, 0), -1)
                cv2.circle(frame, index_tip, 10, (0, 255, 0), -1)
            else:
                volume_control.reset()
            
            # Draw volume indicator at palm
            draw_volume_bar(frame, volume_control.volume, palm)
            
            # Status text
            if volume_control.is_controlling:
                cv2.putText(frame, "CONTROLLING", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Pinch to control", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow('Air Volume Control', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = toggle_fullscreen('Air Volume Control', fullscreen)
    
    tracker.release()

if __name__ == "__main__":
    main()

