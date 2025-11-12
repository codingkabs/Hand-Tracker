"""
Feature 5: Virtual Hand Drawing
Draw in the air with your finger - different gestures change colors
"""
import cv2
import numpy as np
from base import HandTracker

class VirtualCanvas:
    def __init__(self, width, height):
        self.canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White canvas
        self.current_color = (0, 0, 255)  # Red by default
        self.colors = [
            (0, 0, 255),    # Red
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
            (255, 255, 0),  # Cyan
        ]
        self.color_index = 0
        self.last_point = None
        self.drawing = False
    
    def change_color(self):
        """Cycle to next color"""
        self.color_index = (self.color_index + 1) % len(self.colors)
        self.current_color = self.colors[self.color_index]
    
    def draw_point(self, point, thickness=5):
        """Draw a point on canvas"""
        if point is None:
            return
        
        if self.last_point is not None and self.drawing:
            cv2.line(self.canvas, self.last_point, point, self.current_color, thickness)
        else:
            cv2.circle(self.canvas, point, thickness, self.current_color, -1)
        
        self.last_point = point
    
    def clear(self):
        """Clear the canvas"""
        self.canvas = np.ones_like(self.canvas) * 255
        self.last_point = None

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Virtual Drawing - Press ESC to exit")
    print("Controls:")
    print("  - Index finger up: Draw")
    print("  - Fist: Clear canvas")
    print("  - Open hand: Change color")
    print("  - V gesture: Erase mode")
    
    canvas = VirtualCanvas(1280, 720)
    erase_mode = False
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Resize frame to match canvas
        frame = cv2.resize(frame, (1280, 720))
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            index_tip = landmarks['index_tip']
            finger_count = tracker.get_finger_count(landmarks)
            
            # Gesture controls
            if finger_count == 0:  # Fist - Clear
                canvas.clear()
                cv2.putText(frame, "CLEARED!", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            elif finger_count == 5:  # Open hand - Change color
                canvas.change_color()
                cv2.putText(frame, "COLOR CHANGED!", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, canvas.current_color, 3)
            elif finger_count == 2:  # V gesture - Toggle erase
                if tracker.is_finger_up(landmarks, 'index') and tracker.is_finger_up(landmarks, 'middle'):
                    erase_mode = not erase_mode
                    cv2.putText(frame, f"ERASE: {'ON' if erase_mode else 'OFF'}", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            
            # Drawing mode
            if tracker.is_finger_up(landmarks, 'index') and finger_count <= 2:
                canvas.drawing = True
                if erase_mode:
                    # Erase mode - draw white
                    cv2.circle(canvas.canvas, index_tip, 20, (255, 255, 255), -1)
                else:
                    # Draw mode
                    canvas.draw_point(index_tip, thickness=8)
            else:
                canvas.drawing = False
                canvas.last_point = None
        
        # Blend canvas with camera feed
        alpha = 0.7
        blended = cv2.addWeighted(frame, 1-alpha, canvas.canvas, alpha, 0)
        
        # Show current color indicator
        color_rect = np.zeros((50, 200, 3), dtype=np.uint8)
        color_rect[:] = canvas.current_color
        blended[10:60, 10:210] = color_rect
        cv2.putText(blended, "Color", (220, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show mode
        mode_text = "ERASE MODE" if erase_mode else "DRAW MODE"
        cv2.putText(blended, mode_text, (50, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow('Virtual Drawing', blended)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

