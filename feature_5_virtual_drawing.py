"""
Feature 5: Virtual Hand Drawing
Draw in the air with your finger - different gestures change colors
"""
import cv2
import numpy as np
from base import HandTracker
from fullscreen_helper import setup_fullscreen_window, resize_frame_for_fullscreen, toggle_fullscreen

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
    print("Press 'F' to toggle fullscreen")
    print("Controls:")
    print("  - Index finger up: Draw")
    print("  - Fist: Toggle erase/draw mode")
    print("  - Open hand (5 fingers): Change color")
    
    fullscreen = setup_fullscreen_window('Virtual Drawing', start_fullscreen=False)
    canvas = VirtualCanvas(1920, 1080)  # Match fullscreen size
    erase_mode = False
    last_finger_count = 0
    last_fist_state = False
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Resize canvas to match frame
        if frame.shape[:2] != canvas.canvas.shape[:2]:
            canvas.canvas = cv2.resize(canvas.canvas, (frame.shape[1], frame.shape[0]))
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            index_tip = landmarks['index_tip']
            finger_count = tracker.get_finger_count(landmarks)
            
            # Gesture controls with debounce
            # Fist (0 fingers) - Toggle erase/draw mode
            if finger_count == 0:
                if not last_fist_state:  # Only toggle once when fist is first made
                    erase_mode = not erase_mode
                    last_fist_state = True
                    cv2.putText(frame, f"MODE: {'ERASE' if erase_mode else 'DRAW'}", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            else:
                last_fist_state = False
            
            # Open hand (5 fingers) - Change color (only once per gesture)
            if finger_count == 5 and last_finger_count != 5:
                canvas.change_color()
                cv2.putText(frame, "COLOR CHANGED!", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, canvas.current_color, 3)
            
            last_finger_count = finger_count
            
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
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = toggle_fullscreen('Virtual Drawing', fullscreen)
    
    tracker.release()

if __name__ == "__main__":
    main()

